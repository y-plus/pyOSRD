import base64
import os
import requests
import shutil

from typing import Protocol

import networkx as nx
import PIL

from PIL.JpegImagePlugin import JpegImageFile


class OSRD(Protocol):
    trains: list[int | str]

    def path(train: int | str):
        ...


@property
def graph(self: OSRD) -> nx.DiGraph:

    edges = set()
    for train, _ in enumerate(self.trains):
        traj = self.path(train)
        edges = edges.union({
            (traj[i], traj[i+1])
            for i in range(len(traj)-1)
            })

    G = nx.DiGraph(edges)

    dict = {
        u: v
        for u, v in zip(
            self.df.index,
            self.df.infer_objects(copy=False).fillna(0).values
        )
    }

    nx.set_node_attributes(G, dict, 'times')

    return G


def _mermaid_graph(self: OSRD) -> str:
    return "graph LR;"+";".join([
        f"{str(edge[0]).replace('<','').replace('>','')}"
        f"-->{str(edge[1]).replace('<','').replace('>','')}"
        for edge in self.graph.edges
    ])


def draw_graph(
    self,
    save: str | None = None,
) -> JpegImageFile:
    graphbytes = _mermaid_graph(self).encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    url = "https://mermaid.ink/img/" + base64_string

    response = requests.get(url, stream=True)

    with open('tmp.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    image = PIL.Image.open('tmp.png')

    if save:
        os.rename('tmp.png', save)
    else:
        os.remove('tmp.png')

    return image
