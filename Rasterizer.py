from gl import Renderer, P2, P3, color
import shaders

width=450
height=450
render=Renderer(width,height)
render.cfondo()
render.vShader=shaders.vShader
render.glMirar(cpos=(0,-1,2), epos=(0,0,0))
render.glLuzdir(1,-1,1)
render.glLoadM("./modelo/perro.obj", "./textura/perro.bmp",trans=(0,0,0), rotar=(0,0,0), escala=(0.5,0.5,0.5))
render.glRender()

render.glFinish("output.bmp")