# -*- coding: utf-8 -*-
"""Roda DENTRO do Blender. Levanta um pavimento tipo a partir da planta
vetorizada e o empilha N vezes com malha compartilhada.

Ajuste LOBULOS, H_PAV e Z_BASE para o projeto antes de rodar.

Malha compartilhada (obj.copy() + copia.data = obj.data) e o que torna 27
pavimentos baratos: um andar tem ~400 objetos, mas so uma copia da geometria
existe na memoria. duplicate() copiaria a malha 27 vezes sem necessidade.
"""
import bpy, bmesh, json, os, mathutils

PASTA = os.environ.get("PLANTA3D_TORRE", r"C:\planta-3d\torre")
# Os tres lobulos nao sobem a mesma altura. O perfil do topo na elevacao
# ortografica (render 04) mostra tres patamares: dois quase juntos e um
# 7,8 pavimentos mais baixo, que e tambem o volume mais estreito -- portanto o
# lobulo menor da planta (o do APTO_03, a leste).
# Faixa em X (metros, no referencial do modelo) -> numero de pavimentos.
LOBULOS = [(-99.0, -32.0, 27, "A_oeste"),
           (-32.0, -15.5, 27, "B_centro"),
           (-15.5,  99.0, 20, "C_leste")]
N_PAV   = max(l[2] for l in LOBULOS)
H_PAV   = 3.15      # PREMISSA - nao ha corte no pacote; ver relatorio
Z_BASE  = 16.20     # topo do embasamento (Lazer 02 em 12.60 + pe-direito 3.60)
COLECAO = "06_Torre"

G  = json.load(open(os.path.join(PASTA, "geometria_filtrada.json")))
GL = json.load(open(os.path.join(PASTA, "lajes.json")))

COR = {"laje":       ((0.80, 0.78, 0.74, 1), 0.25, -0.25),
       "parede":     ((0.60, 0.59, 0.57, 1), H_PAV - 0.25, 0.0),
       "mobiliario": ((0.52, 0.48, 0.44, 1), 0.55, 0.01),
       "madeira":    ((0.60, 0.44, 0.28, 1), 0.00, 0.02),
       "vegetacao":  ((0.34, 0.49, 0.27, 1), 0.30, 0.01),
       "areia":      ((0.86, 0.79, 0.61, 1), 0.00, 0.02),
       "agua":       ((0.28, 0.53, 0.66, 1), 0.00, 0.01)}


def mat(classe):
    m = bpy.data.materials.get("mat_" + classe)
    if m is None:
        m = bpy.data.materials.new("mat_" + classe); m.diffuse_color = COR[classe][0]
    return m


def peca(nome, pts, z, alt, classe, col):
    if len(pts) < 3: return None
    me = bpy.data.meshes.new(nome); ob = bpy.data.objects.new(nome, me)
    bm = bmesh.new()
    try:
        f = bm.faces.new([bm.verts.new((p[0], p[1], z)) for p in pts])
    except ValueError:
        bm.free(); bpy.data.meshes.remove(me); return None
    if alt > 0:
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        ev = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=ev, vec=(0, 0, alt))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    me.materials.append(mat(classe)); col.objects.link(ob)
    return ob


def build():
    antiga = bpy.data.collections.get(COLECAO)
    if antiga:
        for o in list(antiga.all_objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(antiga)
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)

    col = bpy.data.collections.new(COLECAO)
    bpy.context.scene.collection.children.link(col)

    base = []
    for poly in GL["niveis"]["T"]["laje"]:
        o = peca("Torre_Laje", poly, Z_BASE + COR["laje"][2], COR["laje"][1], "laje", col)
        if o: base.append(o)
    for classe, lista in G["niveis"]["T"]["elementos"].items():
        if classe not in COR: continue
        _, alt, dz = COR[classe]
        for i, el in enumerate(lista):
            o = peca(f"Torre_{classe}_{i}", el["pts"], Z_BASE + dz, alt, classe, col)
            if o: base.append(o)
    print(f"  pavimento tipo: {len(base)} objetos")

    def lobulo(o):
        x = sum((o.matrix_world @ mathutils.Vector(c)).x for c in o.bound_box) / 8.0
        for x0, x1, n, nome in LOBULOS:
            if x0 <= x < x1: return n, nome
        return N_PAV, "?"

    conta = {}
    for o in base:
        n, nome = lobulo(o)
        conta[nome] = conta.get(nome, 0) + 1
        for pav in range(1, n):
            c = o.copy(); c.data = o.data          # malha compartilhada
            c.location.z += pav * H_PAV
            c.name = f"{o.name}_pav{pav+1:02d}"
            col.objects.link(c)
        o.name = o.name + "_pav01"
    for x0, x1, n, nome in LOBULOS:
        print(f"  lobulo {nome:9s} X[{x0:6.1f},{x1:6.1f})  {n:2d} pavimentos  "
              f"topo {Z_BASE + n * H_PAV:6.2f} m   {conta.get(nome,0)} objetos por andar")
    print(f"  torre: {len(col.all_objects)} objetos")


build()
