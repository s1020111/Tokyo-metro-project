import osmium as o
import sys
from haversine import haversine, Unit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from io import StringIO, BytesIO

class RelationHandler(o.SimpleHandler):
    relation_way_dict = {}
    relation_node_dict = {}
    def __init__(self):
        super(RelationHandler, self).__init__()
    def relation(self, w):
        way_id_list = []
        node_id_list = []
        for member in w.members:
            if member.type == 'w' and member.role == '':
                way_id_list.append(member.ref)
            if member.type == 'n':
                #print(member.ref)
                node_id_list.append(member.ref)
                #print(node_id_list)
        #print(w.id)
        RelationHandler.relation_way_dict[w.tags.get('ref')] = way_id_list
        RelationHandler.relation_node_dict[w.tags.get('ref')] = node_id_list

class Node:
    def __init__(self, id, name, location, ref, isTransferStation, stop):
        self.id = id
        self.name = name
        self.location = location
        self.ref = ref
        self.isTransferStation = isTransferStation
        self.stop = stop
all_node_list = []

class NodeHandler(o.SimpleHandler):
    newlist = []
    def __init__(self):
        super(NodeHandler, self).__init__()
    def node(self, w):
        #if w.tags.get('ref') == None and w.tags.get('name') != None:
            #print(w.tags.get('name'))
        #if w.tags.get('ref') != None:
        all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('railway')))



class WayHandler(o.SimpleHandler):
    all_way_dict = {}
    def __init__(self):
        super(WayHandler, self).__init__()
    def way(self, w):
        node_id_list = []
        for node in w.nodes:
            node_id_list.append(node.ref)
        WayHandler.all_way_dict[w.id] = node_id_list
idx = o.index.create_map("sparse_file_array")
R = RelationHandler()
G = WayHandler()
H = NodeHandler()

R.apply_file('export.osm')
G.apply_file('export.osm')
H.apply_file('export.osm')

#print(all_node_list)
#print(WayHandler.all_way_dict)




#print(RelationHandler.relation_way_dict)
class Relation_way:
    def __init__(self,id,big_list):
        self.id = id
        self.big_list = big_list



for x,y in zip(range(0,len(all_node_list)-1),range(1,len(all_node_list))):
    if all_node_list[x].name == all_node_list[y].name:
        all_node_list[x].isTransferStation = True
        all_node_list[y].isTransferStation = True
all_way_list = []
for key in RelationHandler.relation_way_dict.keys():
    way_list =[]
    for way_id in WayHandler.all_way_dict.keys():
        if way_id in RelationHandler.relation_way_dict[key]:
            way_list.append(WayHandler.all_way_dict[way_id])
    all_way_list.append(Relation_way(key,way_list))
call = 0

count = 1
#print(all_way_list[0].id)


'''
    for way in all_way_list[0].big_list:
        for i in range(1,len(way)):
            if way[i] == 1926376085:
                while 1 <= count < len(all_way_list[0].big_list) and all_way_list[0].big_list[count] != way:
                    if way[-1] == all_way_list[0].big_list[count][0]:
                        way.pop()
                        way += all_way_list[0].big_list[count]
                        #print(way)
                        count = 0
                    count += 1
            #print(len(way))
                for j in range(1,len(way)):
                    if way[j] == 1926376082:
                        way  = way[i:j+1]
                        print(way)
                        break
                break

'''
def ReturnWay(Node1,Node2):
    '''
    input : Two nodes station that are next to each other
    output : a list of nodes that connect two stations
    '''
    count = 0
    for relation_count in range(len(all_way_list)):
        for way in all_way_list[relation_count].big_list:
            for i in range(1,len(way)):
                if way[i] == Node1:
                    #print(way)
                    #print(len(all_way_list[relation_count].big_list))
                    way_index = all_way_list[relation_count].big_list.index(way)
                    while 0 <= count < len(all_way_list[relation_count].big_list):
                        #print(all_way_list[relation_count].big_list[count][0])
                        if count == way_index:
                            count += 1
                            continue
                        if way[-1] == all_way_list[relation_count].big_list[count][0]:
                            way.pop()
                            way += all_way_list[relation_count].big_list[count]
                            #print(way)
                            count = 0
                        count += 1
                    count = 0
                    while 0 <= count < len(all_way_list[relation_count].big_list):
                        if count == way_index:
                            count += 1
                            continue
                        if way[0] == all_way_list[relation_count].big_list[count][-1]:
                            way.pop(0)
                            way = all_way_list[relation_count].big_list[count] + way
                            #print(way)
                            count = 0
                        count += 1
                    #print(way)
                    
                    if way.index(Node1) > way.index(Node2):
                        way = way[way.index(Node2):way.index(Node1)+1]
                    else:
                        way = way[way.index(Node1):way.index(Node2)+1]
                    return way

def countWaydistance(way):
    '''
    input : a list of node_id
    output : sum of distance between neighbor nodes
    '''
    geometry_list = []
    distance = 0
    for node_id in way:
        for node in all_node_list:
            if node.id == node_id:
                geometry_list.append((node.location.lat,node.location.lon))
    for i,j in zip(range(len(geometry_list)),range(1,len(geometry_list))):
        distance += haversine(geometry_list[i], geometry_list[j], unit = 'm')
    return distance

def get_node_id(node_ref):
    '''
    input : node reference (ex:G04, H03)
    output : node id
    '''
    for node in all_node_list:
        if node.ref == node_ref:
            return node.id

def get_node_type(node_id):
    '''
    input : node id
    output : node type switch boolean
    '''
    for node in all_node_list:
        if node.id == node_id:
            if node.stop == 'switch':
                return False
'''
def get_ref(name):
    search_elem[0].send_keys(Keys.CONTROL + "a")
    search_elem[0].send_keys(Keys.DELETE)
    # XQuery language
    # Overpass QL
    search_elem[0].send_keys('[out:xml][timeout:25];' +           # output format:xml                               
    '(' + 'node["name"="'+
     name +
     '"]["station" = "subway"]\n' +
    '(35.4,139.5,36.0,140.0);\n' +
    '); \
    out; \
    >; \
    out skel qt; \
    ')

    # Run overpass API
    search_elem[0].send_keys(Keys.CONTROL,Keys.ENTER)
    time.sleep(5)
    search_elem[1].send_keys(Keys.CONTROL + "a")
    new = search_elem[1].get_attribute('value').split('ref')
    try:
        return new[1].split('"')[2]
    except IndexError:
        return 'No reference'


def ref_update(name,ref):
    for elem in root.findall('.//node'):
        if elem.findall('.//tag[@v = "'+ name +'"]'):
            if elem.findall('.//tag[@v = "ref"]'):
                break
            else:
                ref_element = etree.Element('tag', {'k':'ref','v':ref})
                elem.append(ref_element)
    tree.write('export.osm',encoding="utf-8",pretty_print=True)
'''
del_way_list =[]
for way in WayHandler.all_way_dict.keys():
    #print(get_node_type(WayHandler.all_way_dict[way][0]))
    if get_node_type(WayHandler.all_way_dict[way][0]) == True and get_node_type(WayHandler.all_way_dict[way][-1]) == True:
        del_way_list.append(way)

for way in del_way_list:
    del WayHandler.all_way_dict[way]





get_ref_node_list =[]
# find station without reference
for node in all_node_list:
    if node.ref == None and node.stop == 'stop':
        get_ref_node_list.append(node.name)

get_ref_node_list = list(set(get_ref_node_list))
#print(get_ref_node_list)

# split station with multiple reference
def ref_split(node):
    '''
    input: class object Node
    output: None, change class object Node's reference to its belongings
    '''
    if ';' in str(node.ref):
        ref_list = node.ref.split(';')
        node.ref = []
        for rel_id in RelationHandler.relation_node_dict.keys():
            if node.id in RelationHandler.relation_node_dict[rel_id]:
                for ref in ref_list:
                    if str(rel_id) in ref:
                        node.ref.append(ref)
        if len(node.ref) == 1 :
            node.ref = ''.join(node.ref)
            print(node.ref)
        else :
            node.ref = ';'.join(node.ref)
            print(node.ref)




for node in all_node_list:
    ref_split(node)






G_list = ['G04','G05','G06','G07','G08','G09','G10','G11','G12','G13','G14','G15','G16','G17','G18','G19']
G_distance_list =[]

#print(get_node_id(G_list[1]))
for i,j in zip(range(len(G_list)-1),range(1,len(G_list))):
    G_distance_list.append(countWaydistance(ReturnWay(get_node_id(G_list[i]),get_node_id(G_list[j]))))

#print(G_distance_list)



# Test
#print(countWaydistance(ReturnWay(get_node_id('F13'),get_node_id('F14'))))



'''
1926376082
for i in range(len(all_way_list)):
    call = 0
    for j in range(len(all_way_list[i].big_list)):
            for k in range(len(all_way_list[i].big_list[j])):
                call += 1

    print(str(call) +  'call')
    count = 1
    while 1 <= count < len(all_way_list[i].big_list):
        #print(all_way_list[i].big_list[k][0])
        if all_way_list[i].big_list[0][-1] == all_way_list[i].big_list[count][0]:
            all_way_list[i].big_list[0].pop()
            all_way_list[i].big_list[0] += all_way_list[i].big_list[count]
            count = 0
        if all_way_list[i].big_list[0][0] == all_way_list[i].big_list[count][-1]:
            all_way_list[i].big_list[0].pop(0)
            all_way_list[i].big_list[0] = all_way_list[i].big_list[count] + all_way_list[i].big_list[0]
            count = 0        
        count += 1
print(all_way_list[1].big_list[0])

#print(all_way_list[0].big_list[0])
#for node in all_node_list:
    #if node.isTransferStation == True:
        #print(node.ref)
rel_way_dict = {}

for key in RelationHandler.relation_way_dict.keys():
    for value in RelationHandler.relation_way_dict[key]:
        for w in WayHandler.all_way_list:
        #print(type(value))
        #print(type(w.id))
            if w.id == value:
                rel_way_list.append(w)
                #print(rel_way_list)
                print(1)
    rel_way_dict[key] = rel_way_list
'''