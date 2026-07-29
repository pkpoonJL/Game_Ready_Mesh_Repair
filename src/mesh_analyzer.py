from pathlib import Path
from typing import TypeAlias
from math import sqrt
import pandas as pd
import trimesh
SUPPORTED_EXTENSIONS = {".obj", ".ply", ".stl", ".glb", ".gltf"}
Vec3: TypeAlias = tuple[float, float, float]
MeshMetrics: TypeAlias = tuple[int, int, int]
def cross(vector_1:Vec3,vector_2:Vec3)->Vec3:
    u1,u2,u3=vector_1
    v1,v2,v3=vector_2
    return u2*v3-u3*v2,u3*v1-u1*v3,u1*v2-u2*v1
def norm(vector_1:Vec3)->float:
    dx,dy,dz=vector_1
    return sqrt(dx*dx+dy*dy+dz*dz)
def load_as_mesh(path:Path)->trimesh.Trimesh:
    loaded = trimesh.load(path, force=None)
    if isinstance(loaded, trimesh.Scene):#case:multiple meshes
        meshes=[]
        for geo_object in loaded.geometry.values():
            if isinstance(geo_object,trimesh.Trimesh):
                meshes.append(geo_object)
        if not meshes: raise ValueError(f"No mesh geometry found in scene: {path}")
        return trimesh.util.concatenate(meshes)
    if isinstance(loaded,trimesh.Trimesh):#case:single mesh
        return loaded
    raise TypeError(f"Unsupported loaded object type: {type(loaded)}")#case object type not supported
def build_edge_count(faces)->dict[Vec3]:
    #enumerate faces
    edge_count={}#empty map for counting
    for face in faces:#face=[int,int,int]
        a,b,c=int(face[0]),int(face[1]),int(face[2])
        #create pairs
        edges=[(a,b),(b,c),(c,a)]
        for Edge in edges:
            v1,v2=Edge
            if v1>v2:
                v1,v2=v2,v1
            e=(v1,v2)
            if e not in edge_count:
                edge_count[e]=0
            edge_count[e]+=1
    return edge_count
def count_boundary_edges(mesh:trimesh.Trimesh)->int:
    faces=mesh.faces
    edge_count=build_edge_count(faces)
    boundary_edges=0
    for edge,count in edge_count.items():
        if count==1:
            boundary_edges+=1
    return boundary_edges
def count_nonmanifold_edges(mesh:trimesh.Trimesh)->int:
    faces=mesh.faces
    edge_count=build_edge_count(faces)
    nonmanifold_edges_count=0
    for edge,count in edge_count.items():
        if count>2:
            nonmanifold_edges_count+=1
    return nonmanifold_edges_count
def count_degenerate_faces(mesh:trimesh.Trimesh, eps:float=1e-12)->int:
    faces=mesh.faces
    degenerate_face_count=0
    for face in faces:
        ia,ib,ic =int(face[0]),int(face[1]),int(face[2])
        ax,ay,az=mesh.vertices[ia]
        bx,by,bz=mesh.vertices[ib]
        cx,cy,cz=mesh.vertices[ic]
        vector_ab=(bx-ax,by-ay,bz-az)
        vector_ac=(cx-ax,cy-ay,cz-az)
        area=0.5*norm(cross(vector_ab,vector_ac))
        if area<eps:
            degenerate_face_count+=1
    return degenerate_face_count
def analyze_mesh(mesh:trimesh.Trimesh,eps:float=1e-12)->MeshMetrics:
    boundary_edges=count_boundary_edges(mesh)
    nonmanifold_edges=count_nonmanifold_edges(mesh)
    degenerate_face_count=count_degenerate_faces(mesh, eps)
    return boundary_edges,nonmanifold_edges,degenerate_face_count
def print_metrics(metrics: MeshMetrics) -> None:
    boundary_edges,nonmanifold_edges,degenerate_faces=metrics
    print("boundary_edges:", boundary_edges)
    print("nonmanifold_edges:", nonmanifold_edges)
    print("degenerate_faces:", degenerate_faces)
def main()->None:
    if __name__ == "__main__":
        main()