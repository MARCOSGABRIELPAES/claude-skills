# -*- coding: utf-8 -*-
"""Roda DENTRO do Blender. Le lajes.json + geometria_filtrada.json e levanta
o modelo. Somente geometria: sem luz, sem material de render, sem textura.

Chame do MCP assim (o namespace nao persiste entre chamadas, entao rodar o
arquivo do disco e mais confiavel que colar o codigo):

    import runpy; runpy.run_path(r"<caminho>\constroi_blender.py", run_name="__main__")

O caminho da pasta de trabalho vem da variavel PASTA abaixo -- ajuste antes.
"""
import bpy, bmesh, json, os

PASTA = os.environ.get("PLANTA3D_PASTA", r"C:\planta-3d")

CFG = json.load(open(os.path.join(PASTA, "projeto.json"), encoding="utf-8"))
G   = json.load(open(os.path.join(PASTA, "geometria_filtrada.json")))
GL  = json.load(open(os.path.join(PASTA, "lajes.json")))

# classe -> (cor de viewport, altura de extrusao, deslocamento em Z a partir do piso)
COR = {"laje":       ((0.78, 0.76, 0.72, 1), 0.30, -0.30),
       "parede":     ((0.58, 0.57, 0.55, 1), 2.70,  0.00),
       "mobiliario": ((0.50, 0.46, 0.42, 1), 0.55,  0.01),
       "vaga":       ((0.62, 0.70, 0.70, 1), 0.00,  0.015),
       "agua":       ((0.28, 0.53, 0.66, 1), 1.15, -1.30),
       "areia":      ((0.86, 0.79, 0.61, 1), 0.00,  0.02),
       "vegetacao":  ((0.34, 0.49, 0.27, 1), 0.30,  0.01),
       "madeira":    ((0.58, 0.42, 0.26, 1), 0.00,  0.03)}


def limpa():
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)     # preserva camera e luz
    for c in list(bpy.data.collections):
        if len(c.all_objects) == 0:
            bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials):
        for m in list(blk):
            if m.users == 0:
                blk.remove(m)


def mat(classe):
    m = bpy.data.materials.get("mat_" + classe)
    if m is None:
        m = bpy.data.materials.new("mat_" + classe)
        m.diffuse_color = COR[classe][0]
    return m


def peca(nome, pts, z, alt, classe, col):
    if len(pts) < 3:
        return None
    me = bpy.data.meshes.new(nome)
    ob = bpy.data.objects.new(nome, me)
    bm = bmesh.new()
    try:
        f = bm.faces.new([bm.verts.new((p[0], p[1], z)) for p in pts])
    except ValueError:                       # poligono degenerado ou repetido
        bm.free(); bpy.data.meshes.remove(me); return None
    if alt > 0:
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        ev = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=ev, vec=(0, 0, alt))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    me.materials.append(mat(classe))
    col.objects.link(ob)
    return ob


def recorta_piscinas(lajes, aguas, z, col):
    """Abre o vazio das piscinas na laje para a lamina aparecer rebaixada."""
    if not lajes or not aguas:
        return
    me = bpy.data.meshes.new("_cortador")
    cut = bpy.data.objects.new("_cortador", me)
    bm = bmesh.new()
    for el in aguas:
        pts = el["pts"]
        if len(pts) < 3:
            continue
        try:
            f = bm.faces.new([bm.verts.new((p[0], p[1], z - 2.0)) for p in pts])
        except ValueError:
            continue
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        ev = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=ev, vec=(0, 0, 4.0))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    col.objects.link(cut)
    for laje in lajes:
        mo = laje.modifiers.new("corte", 'BOOLEAN')
        mo.operation = 'DIFFERENCE'; mo.object = cut
        mo.solver = 'FLOAT'          # em Blender 5.x os solvers sao FLOAT/EXACT/MANIFOLD
        bpy.context.view_layer.objects.active = laje
        try:
            bpy.ops.object.modifier_apply(modifier=mo.name)
        except Exception as e:
            print("  boolean falhou:", e); laje.modifiers.remove(mo)
    bpy.data.objects.remove(cut, do_unlink=True)


def build():
    limpa()
    for cod, nv in CFG["niveis"].items():
        z = nv["z"]
        rot = nv.get("rotulo", cod)
        col = bpy.data.collections.new(rot)
        bpy.context.scene.collection.children.link(col)
        lajes = []
        for poly in GL["niveis"][cod]["laje"]:
            o = peca(f"{rot}_Laje", poly, z + COR["laje"][2], COR["laje"][1], "laje", col)
            if o:
                lajes.append(o)
        dados = G["niveis"][cod]["elementos"]
        recorta_piscinas(lajes, dados.get("agua", []), z, col)
        for classe, lista in dados.items():
            if classe not in COR:
                continue
            _, alt, dz = COR[classe]
            for i, el in enumerate(lista):
                peca(f"{rot}_{classe}_{i}", el["pts"], z + dz, alt, classe, col)
        print(f"  {rot:16s} z={z:6.2f}  objetos={len(col.all_objects)}")


build()
