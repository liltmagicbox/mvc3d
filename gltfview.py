"""gltfview.py -- freeze the world into a .glb file. blender / unreal / three.js all read it.

we already stream pos/rot/scale to the three.js view over websocket.
gltf is the same view-data idea, but frozen into a standard file:
transforms + geometry + materials + lights + camera, one .glb.

actor mapping:
	actor.pos / rot / scale  -> node TRS  (rot: euler xyz radians -> quaternion inside)
	actor.geo  -> mesh. attrs dict ({'position':..,'index':..}) or Geometry-like (.attrs)
	actor.mat  -> material. dict of gltf add_material kwargs: {'color':0xff8800,'roughness':0.5}
	no geo     -> empty node, transform only (still lands in blender as an empty)
	extras     -> id/type/speed ride along. blender: custom properties, three.js: userData

use:
	from gltfview import export_actors
	export_actors(world.actors.values(), 'snapshot.glb')
"""

import gltf


def export_actors(actors, path, name='mvc3d_world', up='+Z'):
	g = gltf.Gltf(name=name, up=up, generator='mvc3d.gltfview')
	geo_cache = {}
	mat_cache = {}

	for actor in actors:
		mesh = None
		geo = getattr(actor, 'geo', None)
		if geo is not None:
			attrs = getattr(geo, 'attrs', geo)  # Geometry object or plain dict
			mat = getattr(actor, 'mat', None)
			mat_idx = None
			if mat:
				mat_key = tuple(sorted(mat.items()))
				if mat_key not in mat_cache:
					mat_cache[mat_key] = g.add_material(**mat)
				mat_idx = mat_cache[mat_key]
			geo_key = (id(attrs), mat_idx)
			if geo_key not in geo_cache:
				geo_cache[geo_key] = g.add_mesh(attrs, material=mat_idx, name=f'geo{len(geo_cache)}')
			mesh = geo_cache[geo_key]

		extras = {'id': actor.id, 'type': actor.type}
		if actor.speed:
			extras['speed'] = list(actor.speed)
		g.add_node(
			name = actor.name or f'{actor.type.lower()}_{actor.id}',
			mesh = mesh,
			pos = tuple(actor.pos),
			rot = tuple(actor.rot),
			scale = tuple(actor.scale),
			extras = extras)

	return g.save(path)


def main():
	from actor import Actor
	from test_gltf import make_cube

	a = Actor()
	a.name = 'boxy'
	a.geo = make_cube()
	a.mat = {'color': 0xff8800}
	a.pos = (0, 0, 1)
	export_actors([a], 'gltf_out_world.glb')
	print('wrote gltf_out_world.glb')


if __name__ == '__main__':
	main()
