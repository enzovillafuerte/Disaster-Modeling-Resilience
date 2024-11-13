import igraph, networkx, numpy, operator, pylab, random, sys


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
    largest_component = max(networkx.connected_components(g), key = len)
    n = len(g.nodes())
    x.append(0)
    y.append(len(largest_component) * 1. / n)
    R = 0.0
    for i in range(1, n):
        g.remove_node(l.pop(0)[0])
        largest_component = max(networkx.connected_components(g), key = len)
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
    x4, y4, VE = eigenvector(infile, recalculate)
    x5, y5, VR = rand(infile)

    pylab.figure(1, dpi = 500)
    pylab.xlabel(r"Fraction of vertices removed ($\rho$)")
    pylab.ylabel(r"Fractional size of largest component ($\sigma$)")
    pylab.plot(x1, y1, "b-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x2, y2, "g-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x3, y3, "r-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x4, y4, "c-", alpha = 0.6, linewidth = 2.0)
    pylab.plot(x5, y5, "k-", alpha = 0.6, linewidth = 2.0)
    pylab.legend((r"Degree ($V = %4.3f$)" %(VD), 
                  "Betweenness ($V = %4.3f$)" %(VB), 
                  "Closeness ($V = %4.3f$)" %(VC), 
                  "Eigenvector ($V = %4.3f$)" %(VE), 
                  "Random ($V = %4.3f$)" %(VR)), 
                 loc = "upper right", shadow = False)

    # Inset showing vulnerability values.
    labels = [r"$D$", r"$B$", r"$C$", r"$E$", r"$R$"]
    V = [VD, VB, VC, VE, VR]
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






# 1st Install this libraries using pip. Check out Quito's code
print("Success")

# Windows: py robustness_analysis.py 'sample_network.gml'
