from meshes.base_mesh import BaseMesh
from meshes.chunk_mesh_builder import build_chunk_mesh
from numba.typed import List

class ChunkMesh(BaseMesh):
    def __init__(self, chunk):
        super().__init__()
        self.engine = chunk.engine
        self.chunk = chunk
        self.ctx = self.engine.ctx
        self.program = self.engine.shader_program.chunk

        self.vbo_format = '1u4'
        self.format_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())
        self.attrs = ('packed_data',) # ('packed_data', self.vbo_format) ??? 
        self.vao = self.get_vao()

    def rebuild(self):
        """Rebuild the mesh data."""

        self.vao = self.get_vao()

    def get_vertex_data(self):
        """Get the vertex data for the mesh."""
        chunk_voxels_ids: list[int] = [voxel.id for voxel in self.chunk.voxels]
        
        # Directly create the numba typed list
        numba_world_voxels_ids = List()
        for chunk in self.chunk.world.voxels:
            numba_sublist = List()
            for voxel in chunk:
                numba_sublist.append(voxel.id)
            numba_world_voxels_ids.append(numba_sublist)

        mesh = build_chunk_mesh( # Numpy array (not explicitly declared because it would require that numpy is imported which is not needed in this file)
            chunk_voxels_ids=chunk_voxels_ids,
            format_size=self.format_size,
            chunk_pos=tuple(map(int, self.chunk.position)), # Convert the position to a tuple of integers (numba cannot handle glm.vec3)
            world_voxels_ids=numba_world_voxels_ids
        )
        return mesh