"""test_gltf.py -- actor world -> .glb -> back, via gltf.py + gltfview.py

run: python3 test_gltf.py
the written world.glb opens in blender (drag&drop), unreal 5 (drag&drop),
or three.js GLTFLoader (the viewer side of this repo).
"""

import os
import math

import gltf
from gltfview import export_actors
from actor import Actor

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gltf_out')


def make_cube(size=1.0):
	"8 verts, 12 tris, smooth normals. the Geo.cube() of fullcode, for real."
	s = size/2
	attrs = {
		'position': [(-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s),
			(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)],
		'index': [0,2,1, 0,3,2, 4,5,6, 4,6,7, 0,1,5, 0,5,4,
			1,2,6, 1,6,5, 2,3,7, 2,7,6, 3,0,4, 3,4,7],
	}
	gltf.calc_normals(attrs)
	return attrs


def test_cube_winding():
	"smooth normals of a cube point outward if winding (CCW) is right."
	attrs = make_cube()
	pos = attrs['position']
	nor = attrs['normal']
	for i,(x,y,z) in enumerate(pos):
		nx,ny,nz = nor[i*3:i*3+3]
		assert x*nx + y*ny + z*nz > 0, f'vert {i} normal points inward'
	print('cube winding: ok (normals outward)')


def test_world_roundtrip():
	cube = make_cube()

	a1 = Actor()
	a1.name = 'crate1'
	a1.geo = cube
	a1.mat = {'color': 0xc87830, 'roughness': 0.8}
	a1.pos = (2, 1, 0.5)
	a1.rot = (0, 0, 0.6)

	a2 = Actor()
	a2.name = 'crate2'
	a2.geo = cube                 # same geo shared -> same mesh in file
	a2.mat = {'color': 0xc87830, 'roughness': 0.8}
	a2.pos = (-1, 2, 0.5)
	a2.scale = (1, 1, 2)
	a2.speed = (0, 3, 0)          # rides along in extras

	a3 = Actor()                  # no geo: transform-only marker node
	a3.name = 'spawnpoint'
	a3.pos = (0, -3, 0)

	os.makedirs(OUT, exist_ok=True)
	fpath = os.path.join(OUT, 'world.glb')
	export_actors([a1, a2, a3], fpath)

	#--- read back
	s = gltf.load(fpath)
	nodes = {n['name']: n for n in s['nodes']}

	n1 = nodes['crate1']
	assert n1['pos'] == (2, 1, 0.5)
	assert all(abs(a-b) < 1e-6 for a,b in zip(n1['rot'], (0, 0, 0.6)))
	n2 = nodes['crate2']
	assert n2['scale'] == (1, 1, 2)
	assert n2['extras']['speed'] == [0, 3, 0]
	assert n2['extras']['type'] == 'Actor'
	assert n1['mesh'] == n2['mesh'], 'shared geo should be one mesh'
	assert 'mesh' not in nodes['spawnpoint']

	mesh = s['meshes'][n1['mesh']]
	attrs = mesh['primitives'][0]['attrs']
	assert len(attrs['position']) == 8*3
	assert len(attrs['index']) == 36
	# and this attrs dict is Geometry-shaped: Geometry(**) / VAO(attrs) ready.

	size = os.path.getsize(fpath)
	print(f'world roundtrip: ok ({size} B, {len(s["nodes"])} nodes)')


def main():
	test_cube_winding()
	test_world_roundtrip()
	print('view the file: blender/UE drag&drop, or three.js GLTFLoader. see GLTF_COMPAT.md')


if __name__ == '__main__':
	main()
