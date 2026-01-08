import os
import time
import SPARQLWrapper
import rdflib
import owlready2

from performance_utils import Backend, LoadingTiming, LatexPerformanceExporter


def evaluate_loading():
    sparql = SPARQLWrapper.SPARQLWrapper("http://localhost:7200/repositories/KRROOD")
    sparql.setReturnFormat(SPARQLWrapper.JSON)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    rdf_file_path = os.path.join(dir_path, "..", "resources", "statements.rdf")

    print("Loading data into owlready2...")
    # TODO perform reasoning
    owlready2_world = owlready2.World()
    start = time.time()
    owlready2_world.get_ontology(rdf_file_path).load()
    owlready2_loading_time = time.time() - start

    print("Loading data into rdflib...")
    rdflib_graph = rdflib.Graph()
    start = time.time()
    rdflib_graph.parse(rdf_file_path, format="xml")
    rdflib_loading_time = time.time() - start

    loading_timing = LoadingTiming(
        backend_runtimes={
            Backend.Owlready2: owlready2_loading_time,
            Backend.RDFLib: rdflib_loading_time,
        }
    )

    exporter = LatexPerformanceExporter(loading_timing=loading_timing)
    exporter.export_loading_performance()


if __name__ == "__main__":
    evaluate_loading()
