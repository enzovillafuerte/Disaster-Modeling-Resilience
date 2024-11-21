import igraph, networkx, numpy, operator, pylab, random, sys
import pandas as pd

# Sample Network to be ingested into the functions
G = networkx.Graph()
G.add_nodes_from(range(1, 16))

# defining edges to form clusters and connect them
edges = [
    (1, 2), (1, 3), (2, 3),  # Cluster 1
    (4, 5), (5, 6), (6, 4), (4, 7),  # Cluster 2 with a bridge node 7
    (8, 9), (9, 10), (10, 8),  # Cluster 3
    (11, 12), (12, 13), (13, 11),  # Cluster 4
    (14, 15),  # Small two-node connection
    (3, 7), (7, 10), (10, 13),  # Bridges connecting clusters
    (1, 14), (5, 15)  # Random links for added robustness
]

# Adding the edges to the graph
G.add_edges_from(edges)

# Save this graph to a GML file to be used in your robustness analysis
networkx.write_gml(G, "sample_network.gml")


##########
# Combined Matrix Output from Optimization Model
##########



###########
###########
##########
def betweenness(infile, recalculate = False):
    """
    Performs robustness analysis based on betweenness centrality,  
    on the network specified by infile using sequential (recalculate = True) 
    or simultaneous (recalculate = False) approach. Returns a list 
    with fraction of nodes removed, a list with the corresponding sizes of 
    the largest component of the network, and the overall vulnerability 
    of the network.
    """

    g = networkx.read_gml(infile)
    m = networkx.betweenness_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    x = []
    y = []
    largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
    n = len(g.nodes())
    x.append(0)
    y.append(len(largest_component) * 1. / n)
    R = 0.0
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.betweenness_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
        x.append(i * 1. / n)
        R += len(largest_component) * 1. / n
        y.append(len(largest_component) * 1. / n)
    return x, y, 0.5 - R / n

def betweenness_fracture(infile, outfile, fraction, recalculate = False):
    """
    Removes given fraction of nodes from infile network in reverse order of 
    betweenness centrality (with or without recalculation of centrality values 
    after each node removal) and saves the network in outfile.
    """

    g = networkx.read_gml(infile)
    m = networkx.betweenness_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    largest_component = max(networkx.connected_components(g), key = len)
    n = len(g.nodes())
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.betweenness_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g), key = len)
        if i * 1. / n >= fraction:
            break
    components = networkx.connected_components(g)
    component_id = 1
    for component in components:
        for node in component:
            g.node[node]["component"] = component_id
        component_id += 1
    networkx.write_gml(g, outfile)

def closeness(infile, recalculate = False):
    """
    Performs robustness analysis based on closeness centrality,  
    on the network specified by infile using sequential (recalculate = True) 
    or simultaneous (recalculate = False) approach. Returns a list 
    with fraction of nodes removed, a list with the corresponding sizes of 
    the largest component of the network, and the overall vulnerability 
    of the network.
    """

    g = networkx.read_gml(infile)
    m = networkx.closeness_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    x = []
    y = []
    largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
    n = len(g.nodes())
    x.append(0)
    y.append(len(largest_component) * 1. / n)
    R = 0.0
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.closeness_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
        x.append(i * 1. / n)
        R += len(largest_component) * 1. / n
        y.append(len(largest_component) * 1. / n)
    return x, y, 0.5 - R / n

def closeness_fracture(infile, outfile, fraction, recalculate = False):
    """
    Removes given fraction of nodes from infile network in reverse order of 
    closeness centrality (with or without recalculation of centrality values 
    after each node removal) and saves the network in outfile.
    """

    g = networkx.read_gml(infile)
    m = networkx.closeness_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    largest_component = max(networkx.connected_components(g), key = len)
    n = len(g.nodes())
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.closeness_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g), key = len)
        if i * 1. / n >= fraction:
            break
    components = networkx.connected_components(g)
    component_id = 1
    for component in components:
        for node in component:
            g.node[node]["component"] = component_id
        component_id += 1
    networkx.write_gml(g, outfile)

def degree(infile, recalculate = False):
    """
    Performs robustness analysis based on degree centrality,  
    on the network specified by infile using sequential (recalculate = True) 
    or simultaneous (recalculate = False) approach. Returns a list 
    with fraction of nodes removed, a list with the corresponding sizes of 
    the largest component of the network, and the overall vulnerability 
    of the network.
    """

    g = networkx.read_gml(infile)
    m = networkx.degree_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    x = []
    y = []
    largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
    n = len(g.nodes())
    x.append(0)
    y.append(len(largest_component) * 1. / n)
    R = 0.0
    for i in range(1, n - 1):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.degree_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
        x.append(i * 1. / n)
        R += len(largest_component) * 1. / n
        y.append(len(largest_component) * 1. / n)
    return x, y, 0.5 - R / n

def degree_fracture(infile, outfile, fraction, recalculate = False):
    """
    Removes given fraction of nodes from infile network in reverse order of 
    degree centrality (with or without recalculation of centrality values 
    after each node removal) and saves the network in outfile.
    """

    g = networkx.read_gml(infile)
    m = networkx.degree_centrality(g)
    l = sorted(m.items(), key = operator.itemgetter(1), reverse = True)
    largest_component = max(networkx.connected_components(g), key = len)
    n = len(g.nodes())
    for i in range(1, n - 1):
        g.remove_node(l.pop(0)[0])
        if recalculate:
            m = networkx.degree_centrality(g)
            l = sorted(m.items(), key = operator.itemgetter(1), 
                       reverse = True)
        largest_component = max(networkx.connected_components(g), key = len)
        if i * 1. / n >= fraction:
            break
    components = networkx.connected_components(g)
    component_id = 1
    for component in components:
        for node in component:
            g.node[node]["component"] = component_id
        component_id += 1
    networkx.write_gml(g, outfile)

def eigenvector(infile, recalculate = False):
    """
    Performs robustness analysis based on eigenvector centrality,  
    on the network specified by infile using sequential (recalculate = True) 
    or simultaneous (recalculate = False) approach. Returns a list 
    with fraction of nodes removed, a list with the corresponding sizes of 
    the largest component of the network, and the overall vulnerability 
    of the network.
    """

    def indexof(g, s):
        vs = g.vs()
        for i in range(0, len(vs)):
            v = vs[i]
            if v["label"] == s:
                return i
        return None

    g = igraph.Graph.Read_GML(infile)
    vs = g.vs()
    m = {}
    el = g.eigenvector_centrality()
    for i in range(0, len(vs)):
        m[vs[i]["label"]] = float(el[i])
    l = m.items()
    l = sorted(l, key = operator.itemgetter(1), reverse = True)
    x = []
    y = []
    largest_component = g.components().giant().vcount()
    n = g.vcount()
    x.append(0)
    y.append(largest_component * 1. / n)
    R = 0.0
    for i in range(1, n):
        g.delete_vertices(indexof(g, l.pop(0)[0]))
        if recalculate:
            m = {}
            el = g.eigenvector_centrality()
            for j in range(0, len(vs)):
                m[vs[j]["label"]] = float(el[j])
            l = m.items()
            l = sorted(l, key = operator.itemgetter(1), reverse = True)
        largest_component = g.components().giant().vcount()
        x.append(i * 1. / n)
        R += largest_component * 1. / n
        y.append(largest_component * 1. / n)
    return x, y, 0.5 - R / n

def eigenvector_fracture(infile, outfile, fraction, recalculate = False):
    """
    Removes given fraction of nodes from infile network in reverse order of 
    eigenvector centrality (with or without recalculation of centrality values 
    after each node removal) and saves the network in outfile.
    """

    def indexof(g, s):
        vs = g.vs()
        for i in range(0, len(vs)):
            v = vs[i]
            if v["label"] == s:
                return i
        return None

    g = igraph.Graph.Read_GML(infile)
    vs = g.vs()
    m = {}
    el = g.eigenvector_centrality()
    for i in range(0, len(vs)):
        m[vs[i]["label"]] = float(el[i])
    l = m.items()
    l = sorted(l, key = operator.itemgetter(1), reverse = True)
    largest_component = g.components().giant().vcount()
    n = g.vcount()
    for i in range(1, n):
        g.delete_vertices(indexof(g, l.pop(0)[0]))
        if recalculate:
            m = {}
            el = g.eigenvector_centrality()
            for j in range(0, len(vs)):
                m[vs[j]["label"]] = float(el[j])
            l = m.items()
            l = sorted(l, key = operator.itemgetter(1), reverse = True)
        largest_component = g.components().giant().vcount()
        if i * 1. / n >= fraction:
            break
    components = g.components()
    component_id = 1
    for component in components:
        for node in component:
            vs[node]["component"] = component_id
        component_id += 1
    g.write_gml(outfile)


# Random attacks in the network simulating potential damages after an earthquake

def rand(infile):
    """
    Performs robustness analysis based on random attack, on the network 
    specified by infile. Returns a list with fraction of nodes removed, a 
    list with the corresponding sizes of the largest component of the 
    network, and the overall vulnerability of the network.
    """

    g = networkx.read_gml(infile)
    l = [(node, 0) for node in g.nodes()]
    random.shuffle(l)
    x = []
    y = []
    largest_component = max(networkx.connected_components(g.to_undirected()), key = len) # To undirected
    n = len(g.nodes())
    x.append(0)
    y.append(len(largest_component) * 1. / n)
    R = 0.0
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        largest_component = max(networkx.connected_components(g.to_undirected()), key = len) ## To undirected
        x.append(i * 1. / n)
        R += len(largest_component) * 1. / n
        y.append(len(largest_component) * 1. / n)
    return x, y, 0.5 - R / n


def main(argv):
    """
    Entry point.
    """

    if len(argv) != 3:
        print("python robustness.py <infile> <outfile> <recalculate>")
        sys.exit(0)

    infile = argv[0]
    outfile = argv[1]
    if argv[2] == "True":
        recalculate = True
    else:
        recalculate = False
    x1, y1, VD = degree(infile, recalculate)
    x2, y2, VB = betweenness(infile, recalculate)
    x3, y3, VC = closeness(infile, recalculate)
    #x4, y4, VE = eigenvector(infile, recalculate)
    x5, y5, VR = rand(infile)

    pylab.figure(1, dpi = 500)
    pylab.xlabel(r"Fraction of vertices removed ($\rho$)")
    pylab.ylabel(r"Fractional size of largest component ($\sigma$)")
    pylab.plot(x1, y1, "b-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x2, y2, "g-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x3, y3, "r-", alpha = 0.6, linewidth = 2.0)
    #pylab.plot(x4, y4, "c-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x5, y5, "k-", alpha = 0.6, linewidth = 2.0)
    pylab.legend((r"Degree ($V = %4.3f$)" %(VD), 
                  "Betweenness ($V = %4.3f$)" %(VB), 
                  "Closeness ($V = %4.3f$)" %(VC), 
                  #"Eigenvector ($V = %4.3f$)" %(VE), 
                  "Random ($V = %4.3f$)" %(VR)), 
                 loc = "upper right", shadow = False)

    # Inset showing vulnerability values.
    # labels = [r"$D$", r"$B$", r"$C$", r"$E$", r"$R$"]
    labels = [r"$D$", r"$B$", r"$C$", r"$R$"]
    # V = [VD, VB, VC, VE, VR]
    V = [VD, VB, VC, VR]
    xlocations = numpy.array(range(len(V)))+0.2
    width = 0.2
    inset = pylab.axes([0.735, 0.45, 0.15, 0.15])
    pylab.bar(xlocations, V, color = ["b", "g", "r", "c", "k"], 
              alpha = 0.6, width = width)
    pylab.yticks([0.0, 0.25, 0.5])
    pylab.xticks(xlocations + width / 2, labels)
    pylab.xlim(0, xlocations[-1] + width * 2)
    pylab.ylabel(r"$V$")

    pylab.savefig(outfile, format = "pdf")
    pylab.close(1)


if __name__ == "__main__":
    main(sys.argv[1:])


# 1st Install this libraries using pip. Check out Quito's code
print("Success")

# Windows: py robustness_analysis.py 'sample_network.gml'
# Mac: python robustness_analysis.py 'sample_network.gml'
# python robustness.py <infile> <outfile> <recalculate>
# python robustness_analysis.py 'sample_network.gml' 'sample_output.pdf' True
# python robustness_analysis.py 'final_network_nobackup.gml' 'final_output_nobk1.pdf' True
# python robustness_analysis.py 'final_network.gml' 'final_output_1.pdf' True
# python robustness_analysis.py 'final_network_MAIN.gml' 'final_output_AA.pdf' True
# python robustness_analysis.py 'final_network_MAIN_OnlyWarehouses.gml' 'final_output_BB.pdf' True

