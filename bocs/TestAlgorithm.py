# User Requirement for all graphs: f1 to f2 (check)
# ******
# Constraint for all graphs: (Sunday)
# 1. Randomly choose a valve or other control component always be closed;
# 2. Or two valve or other control component cannot be opened together

from ConstraintFunctions import findallConnectedNodes
from ConstraintMaker import createRandomConstraint
import AlgorithmComparison
import random
from collections import Counter
import networkx as nx
import os
import numpy as np
import pandas as pd
from networkx.drawing.nx_agraph import read_dot


def getfileList(targetfolderpath):
    Allfile = {}
    NodeList = os.listdir(targetfolderpath)
    for node in NodeList:
        new_path = targetfolderpath + "/" + str(node)
        edgelist = os.listdir(new_path)
        edgelist.sort()
        Allfile[node] = edgelist
    return Allfile


def buildFlowGraph(flow_graph_path):
    # Build flow layer graph g
    g = read_dot(flow_graph_path)
    g = g.to_undirected()
    for edge in g.edges:
        g[edge[0]][edge[1]]['weight'] = int(g.get_edge_data(edge[0], edge[1])['weight'])
    pos = nx.spring_layout(g)
    return g, pos


def locateValveAndCOonFE(vco_path):
    data = pd.read_csv(vco_path, header=None, sep=" ")
    VCOFlist = data.values.tolist()
    VCO2FEdictionary = {}
    FE2VCOdictionary = {}
    for VCO in VCOFlist:
        VCO2FEdictionary[VCO[0]] = VCO[1:]
        tup_temp = tuple(VCO[1:])
        if tup_temp in FE2VCOdictionary.keys():
            FE2VCOdictionary[tup_temp].append(VCO[0])
        else:
            FE2VCOdictionary[tup_temp] = [VCO[0]]
    # data structure of FE2VCOdictionary is like {('F1','F2'): ['V1', 'V2'], ('F1','F3'): ['V3']}
    return VCO2FEdictionary, FE2VCOdictionary


def fp_flag(a, b):
    # true positive
    if a == 1 and b == 1:
        return 1
    # false positive
    if a == 1 and b == 0:
        return 0
    # true negative for bocs, becasue it scaned all the possible graphs
    if a == 0:
        return 2


def checkandappend(nodeslist, b):
    repeatflag = 0
    for n in nodeslist:
        if Counter(n) == Counter(b):
            repeatflag = 1
            break
    if repeatflag == 0:
        nodeslist.append(b)
    return nodeslist


def calculate_false_pos_rate(p1, p2, p3, p4, cl, c1, c2, c3, c4, g_c, flag):
    l1, l2, l3, l4, t1, t2, t3, t4 = 1, 1, 1, 1, 1, 1, 1, 1
    if p1 == -1:
        l1 = 0
    if p2 == -1:
        l2 = 0
    if p3 == -1:
        l3 = 0
    if p4 == -1:
        l4 = 0
    nodeslist = []
    for c in cl:
        if c[0] == 1:
            nodes = findallConnectedNodes([c[1]], g_c.edges())
            for n in nodes:
                if n in c1:
                    t1 = 0
                if n in c2:
                    t2 = 0
                if n in c3:
                    t3 = 0
                if n in c4:
                    t4 = 0
            nodeslist = checkandappend(nodeslist, nodes)
        elif c[0] == 2:
            nodes1 = findallConnectedNodes([c[1]], g_c.edges())
            nodes2 = findallConnectedNodes([c[2]], g_c.edges())
            for n in nodes1:
                for nn in nodes2:
                    if n in c1 and nn in c1:
                        t1 = 0
                    if n in c2 and nn in c2:
                        t2 = 0
                    if n in c3 and nn in c3:
                        t3 = 0
                    if n in c4 and nn in c4:
                        t4 = 0
            nodeslist = checkandappend(nodeslist, nodes1)
            nodeslist = checkandappend(nodeslist, nodes2)
    # true positive = 1, false positive = 0, true negative= = 2, false negative = 3
    t1 = fp_flag(l1, t1)
    t2 = fp_flag(l2, t2)
    t3 = fp_flag(l3, t3)
    if l4 == -2 or flag == -1:
        t4 = 2
    elif flag == 1:
        t4 = 23
    else:
        t4 = fp_flag(l4, t4)
    # other algorithm can find a path without breaking the constraint, that means BOCS is false negative
    if (t1 == 1 or t2 == 1 or t3 == 1) and t4 == 23:
        t4 = 3
    return l1, l2, l3, l4, t1, t2, t3, t4, nodeslist


pos = {}
if __name__ == '__main__':
    # Section loop
    Result_list_metric = ["User Requirement", "Naive estimate", "Dijkstra estimate", "A* estimate", "BOCS estimate",
                          "Naive success", "Dijkstra success", "A* success", "BOCS success",
                          "Constraint List", "Naive control List", "Dijkstra control list", "A star control list", "BOCS control list",
                          "ControlNodesGroup", "Naive path", "Dijkstra path", "A* path", "BOCS path",
                          "Naive path length", "Dijkstra path length", "A* path length",
                          "BOCS path length", "Naive runtime", "Dijkstra runtime", "A* runtime", "BOCS runtime"]
    Result_list_cases = []
    column = []
    for i in range(1, 5):
        Result_list_section = []
        path = f"TestCaseFiles/Section_{i}"
        # Build a dictionary saved all edge info file names as value, keys are the nodes info
        AllDirInOneSection = getfileList(path)
        column = []
        node_num = 0
        constraint_path = f"TestCaseFiles/Constraint_b{i}.csv"
        if os.path.isfile(constraint_path):
            df = pd.read_csv(constraint_path, index_col=0, header=None).squeeze("columns").to_dict()
            constriant = []
            for v in df.values():
                constriant.append(eval(v))
            ConstraintInfoAll = dict(zip(df.keys(), constriant))
        # Nodes info loop
        for NodeInfo in AllDirInOneSection.keys():
            j = 0
            node_num += 1
            GraphListInfo = AllDirInOneSection[NodeInfo]
            # Graph info loop
            jUpperBound = len(AllDirInOneSection[NodeInfo])
            while j < jUpperBound:
                print(f"Sec{i}, Node{node_num}, Edge{int(j/3)+1}")
                index = NodeInfo.index('_')
                column.append(f"Sec{i}|{NodeInfo[:index]}|{GraphListInfo[j][:5]}")
                # remark = GraphListInfo[j][6]
                control_graph_path = f"TestCaseFiles/Section_{i}/{NodeInfo}/{GraphListInfo[j]}"
                flow_graph_path = f"TestCaseFiles/Section_{i}/{NodeInfo}/{GraphListInfo[j + 1]}"
                valve_co_txt = f"TestCaseFiles/Section_{i}/{NodeInfo}/{GraphListInfo[j + 2]}"
                # Build flow layer graph g
                g, pos = buildFlowGraph(flow_graph_path)

                # Create random constraints for each g_c -- control graph
                # Build control layer graph g_c
                g_c = read_dot(control_graph_path)
                g_c = g_c.to_undirected()
                ControlNodes = list(g_c.nodes())
                for edge in g_c.edges:
                    g_c[edge[0]][edge[1]]['weight'] = int(g_c.get_edge_data(edge[0], edge[1])['weight'])
                CPlength = 0
                for node in ControlNodes:
                    if node[0] == 'c' and node[1] != 'o':
                        CPlength += 1
                VandCOlength = len(ControlNodes) - CPlength
                if VandCOlength < 10:
                    ConstraintNum = random.randint(1, VandCOlength)
                else:
                    ConstraintNum = random.randint(1, 10)

                if ConstraintInfoAll:
                    ConstraintList = ConstraintInfoAll[column[-1]]
                else:
                    ConstraintList = createRandomConstraint(ControlNodes, ConstraintNum, VandCOlength)

                # Create a dictionary shows the flow edge on which each valve and other control component locates
                VCO2FEdictionary, FE2VCOdictionary = locateValveAndCOonFE(valve_co_txt)

                # Algorithm comparison
                NaiveTime, NaivePath, NaiveLength = AlgorithmComparison.naive_search(g)
                DijkstraTime, DijkstraPath, DijkstraLength = AlgorithmComparison.dijkstra_search(g)
                AstarTime, AstarPath, AstarLength = AlgorithmComparison.astar_search(g, pos)

                # Update the flow edge info after we get RandomConstraintList and use it in BOCS_search
                g_BOCS = g.copy()
                BOCSTime, BOCSPath, BOCSLength, flagFalseNegative = AlgorithmComparison.BOCS_search(g_BOCS, g_c, pos,
                                                                                ConstraintList, VCO2FEdictionary)

                # Find all valves and other control components which may be involved giving the searched path
                NaiveVCOList = AlgorithmComparison.control_search(NaivePath, FE2VCOdictionary)
                DijkstraVCOList = AlgorithmComparison.control_search(DijkstraPath, FE2VCOdictionary)
                AstarVCOList = AlgorithmComparison.control_search(AstarPath, FE2VCOdictionary)
                BOCSVCOList = AlgorithmComparison.control_search(BOCSPath, FE2VCOdictionary)

                # Find all control edges and control ports being searched in the path
                NaiveControlNodeList, NaiveControlEdgeList = AlgorithmComparison.findall_control_path(NaiveVCOList, g_c)
                DijkstraControlNodeList, DijkstraControlEdgeList = AlgorithmComparison.findall_control_path(DijkstraVCOList, g_c)
                AstarControlNodeList, AstarControlEdgeList = AlgorithmComparison.findall_control_path(AstarVCOList, g_c)
                BOCSControlNodeList, BOCSControlEdgeList = AlgorithmComparison.findall_control_path(BOCSVCOList, g_c)

                # Simulate control and flow layer pathways
                AlgorithmComparison.simulate(NodeInfo, NaiveTime, NaivePath, NaiveControlNodeList, DijkstraTime,
                                             DijkstraPath, DijkstraControlNodeList, AstarTime, AstarPath, AstarControlNodeList,
                                             BOCSTime, BOCSPath, BOCSControlNodeList, i, j, g, g_c, GraphListInfo)

                # Calculate the false positive rate for each algorithm
                Nr, Dr, Ar, Br, t1, t2, t3, t4, nodeslist = calculate_false_pos_rate(NaiveLength, DijkstraLength, AstarLength, BOCSLength,
                ConstraintList, NaiveControlNodeList, DijkstraControlNodeList, AstarControlNodeList, BOCSControlNodeList, g_c,
                                                                                     flagFalseNegative)

                l_currentcase = ["f1 -> f2", Nr, Dr, Ar, Br, t1, t2, t3, t4, ConstraintList, NaiveControlNodeList,
                                 DijkstraControlNodeList, AstarControlNodeList, BOCSControlNodeList, nodeslist,
                                 NaivePath, DijkstraPath, AstarPath, BOCSPath, NaiveLength, DijkstraLength, AstarLength,
                                 BOCSLength, NaiveTime, DijkstraTime, AstarTime, BOCSTime]
                Result_list_section.append(l_currentcase)
                j += 3
                print()

        # NaiveFPR, DijkstraFPR, AstarFPR = calculate_false_pos_rate(Result_list_section) !!!!*****@!!!
        # Result_list_cases.extend(Result_list_section)

        outcsvpath = f"TestCaseFiles/csv_p=50/benchmark-{i}.csv"
        dictionary = dict(zip(column, Result_list_section))
        with open(outcsvpath, 'w', newline='') as f:
            dataframe = pd.DataFrame.from_dict(dictionary, orient='index', columns=Result_list_metric)
            dataframe.to_csv(outcsvpath)
            print()
