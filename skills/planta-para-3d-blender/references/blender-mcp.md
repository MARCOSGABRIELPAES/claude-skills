# Blender via MCP — armadilhas que custam tempo

## O namespace não persiste entre chamadas
Cada `execute_blender_code` roda num escopo novo. Uma função definida numa chamada
não existe na seguinte. Duas saídas:

- **Preferida:** escrever o script em disco e rodar `runpy.run_path(caminho, run_name="__main__")`.
  Além de resolver o problema, deixa o script versionado e reexecutável.
- Para código curto: redefinir tudo na mesma chamada.

## Colocar o viewport numa vista conhecida
Atribuir `region_3d.view_rotation` direto muitas vezes não pega. O caminho confiável
é o operador com contexto sobrescrito:

```python
win = bpy.context.window
for a in win.screen.areas:
    if a.type == 'VIEW_3D':
        reg = [r for r in a.regions if r.type == 'WINDOW'][0]
        with bpy.context.temp_override(window=win, area=a, region=reg):
            bpy.ops.view3d.view_axis(type='TOP')
            bpy.ops.view3d.view_all(center=True)
```

`bpy.ops.view3d.view_all()` sem override falha com *"Expected a view3d region"*.

## Vista de câmera para screenshot
`space.region_3d.view_perspective = 'CAMERA'` precisa ser feito **numa chamada
separada, imediatamente antes** de `get_viewport_screenshot` — senão o screenshot
sai em PERSP. Enquadramento por câmera é mais previsível que mexer em `view_distance`.

Para gerar imagens em arquivo, `bpy.ops.render.opengl(write_still=True)` respeita o
sombreamento sólido do viewport e não precisa de luz nenhuma — ideal quando o
combinado é "só geometria".

## Boolean
Em Blender 5.x os solvers são `FLOAT`, `EXACT`, `MANIFOLD`. `FAST` não existe mais
e levanta enum error. `modifier_apply` exige `view_layer.objects.active` setado.

## Instanciar em massa
Para repetir um pavimento tipo dezenas de vezes, compartilhe a malha em vez de
duplicá-la: `novo = obj.copy(); novo.data = obj.data`. Um andar copiado assim custa
quase nada; `duplicate()` copia a malha e infla o arquivo.

Cuidado com o offset em Z ao copiar de um protótipo já posicionado: se o protótipo
está na cota certa, a cópia entra com `location.z = 0`, não com a diferença de cota.

## Colisão de nomes de coleção
Apagar os objetos de uma coleção não apaga a coleção. Se você recriar com o mesmo
nome, o Blender cria `Nome.001` — e um filtro de visibilidade preso ao nome antigo
esconde tudo. Remova a coleção vazia antes de recriar.

## Animação em Blender 4.4+
`action.fcurves` não existe mais. O caminho é
`action.layers → layer.strips → strip.channelbags → channelbag.fcurves`.

## Z-fighting
Superfícies coplanares piscam. Dê deslocamentos de alguns centímetros por classe
(água −0,05, areia +0,02, deck +0,03, vegetação +0,04) em vez de deixar tudo no
mesmo Z.
