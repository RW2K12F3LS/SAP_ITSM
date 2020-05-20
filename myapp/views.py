from django.shortcuts import render
import json
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User  # django封装好的验证功能
from django.contrib import auth
import joblib
import os
import sys
import pickle
import numpy as np
from .models import get_relation, get_entity
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher


@require_http_methods(["GET"])
def get_answer(request):

    question = request.GET['data']
    relationship = get_relation(question)
    identified_entities = get_entity(question)

    graph = Graph('http://122.51.232.56:7474', username='', password='')

    all_entities = []
    for i in NodeMatcher(graph).match('o'):
        all_entities.append((list(i.items())[0][1]))

    match = []
    for i in all_entities:
        count = 0
        for j in identified_entities:
            if j in i:
                count += 1
        match.append(count)
    identified_entities_backup = []
    if max(match) == 0:  # 全0
        identified_entities_backup = ' '.join(identified_entities).split(' ')
        match = []
        for i in all_entities:
            count = 0
            for j in identified_entities_backup:
                if j.lower() in i.lower():
                    count += 1
            match.append(count)

    def blah():
        return "Please rephrase..."

    while 1:
        count_max = max(match)  # 实体匹配次数
        if count_max == 0:  # 从关系出发+实体相似度
            return JsonResponse(blah(), safe=False)
        count_max_index = match.index(count_max)
        match[count_max_index] = 0

        start_node = all_entities[count_max_index]  # 保证找到需要的实体
        start_node_relations = list(graph.run("match (a:o{content:'" + start_node +"'})-[re]->(b:o) return type(re)").to_table())
        if relationship == 'has_step' and ('has_scenario',) in start_node_relations:
            relationship = 'has_scenario'
        if relationship == 'has_scenario' and ('has_step',) in start_node_relations:
            relationship = 'has_step'
        relationship_exist = False
        for r in start_node_relations:
            if relationship in r[0]:
                relationship_exist = True
                break

        if relationship_exist:
            answer_list = []
            answer_un = graph.run(
                "match (a:o{content:'" + start_node + "'})-[b:" + relationship + "]->(c:o) return c").data()
            for i in answer_un:
                answer_list.append(i['c']['content'])
            answer_list.sort()

            if relationship == 'has_step':  # 如是has_step 那么就自动追加detail如果有,其他只招一级
                for i in answer_list:
                    # 补充detail
                    detail_un = graph.run("match (a:o{content:'" + i + "'})-[b:has_detail]->(c:o) return c").data()
                    for j in detail_un:
                        answer_list.insert(answer_list.index(i) + 1, j['c']['content'])
                # answer_list.append(r"C:\Users\chend\Desktop\ITSM\Investigate_and_Diagnose _GEN_V.pdf#page=4")
                return JsonResponse('\n'.join(answer_list), safe=False)

        # 找不到需要的关系 循环


    # file:///C:/Usxxxxx.pdf#page=4

