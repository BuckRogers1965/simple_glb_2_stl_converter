#!/usr/bin/env python3
"""
Convert glTF (.glb) files to STL
Simplified parser for binary glTF format
"""

import sys
import struct
import json
import numpy as np

def parse_glb(filename):
    """Parse binary glTF (.glb) file"""
    with open(filename, 'rb') as f:
        # Read glTF header (12 bytes)
        magic = f.read(4)
        if magic != b'glTF':
            raise ValueError("Not a valid glTF binary file")
        
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        print(f"glTF version: {version}, Total length: {length} bytes")
        
        # Read JSON chunk header
        chunk_length = struct.unpack('<I', f.read(4))[0]
        chunk_type = f.read(4)
        
        if chunk_type != b'JSON':
            raise ValueError("Expected JSON chunk first")
        
        # Read JSON data
        json_data = f.read(chunk_length)
        scene = json.loads(json_data)
        
        print(f"JSON chunk: {chunk_length} bytes")
        
        # Read BIN chunk header
        chunk_length = struct.unpack('<I', f.read(4))[0]
        chunk_type = f.read(4)
        
        if chunk_type != b'BIN\0':
            raise ValueError("Expected BIN chunk")
        
        # Read binary data
        bin_data = f.read(chunk_length)
        
        print(f"BIN chunk: {chunk_length} bytes")
        
        return scene, bin_data

def extract_mesh_from_glb(scene, bin_data):
    """Extract vertices and faces from glTF scene"""
    
    # Find the mesh data
    mesh_idx = scene['meshes'][0]['primitives'][0]
    positions_accessor = scene['accessors'][mesh_idx['attributes']['POSITION']]
    indices_accessor = scene['accessors'][mesh_idx['indices']]
    
    # Get buffer views
    positions_view = scene['bufferViews'][positions_accessor['bufferView']]
    indices_view = scene['bufferViews'][indices_accessor['bufferView']]
    
    # Extract vertices
    pos_offset = positions_view.get('byteOffset', 0)
    pos_count = positions_accessor['count']
    
    # Read vertices from binary data
    vertices = []
    for i in range(pos_count):
        offset = pos_offset + i * 12  # 3 floats × 4 bytes each
        x, y, z = struct.unpack('<fff', bin_data[offset:offset+12])
        vertices.append([x, y, z])
    
    # Extract faces (indices)
    idx_offset = indices_view.get('byteOffset', 0)
    idx_count = indices_accessor['count']
    
    faces = []
    for i in range(0, idx_count, 3):
        offset = idx_offset + i * 4  # 3 uint32 × 4 bytes each
        a, b, c = struct.unpack('<III', bin_data[offset:offset+12])
        faces.append([a, b, c])
    
    return np.array(vertices), np.array(faces)

def write_stl_binary(vertices, faces, filename):
    """Write binary STL file"""
    with open(filename, 'wb') as f:
        # Header (80 bytes)
        header = b'Converted from glTF/GBL format' + b'\x00' * 50
        f.write(header)
        
        # Number of faces
        f.write(struct.pack('<I', len(faces)))
        
        # Write each face
        for face in faces:
            # Calculate face normal
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            
            # Edge vectors
            u = v1 - v0
            v = v2 - v0
            
            # Cross product for normal
            normal = np.array([
                u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0]
            ])
            
            # Normalize
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal = normal / norm
            
            # Write normal
            f.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
            
            # Write three vertices
            for vertex_idx in face:
                x, y, z = vertices[vertex_idx]
                f.write(struct.pack('<fff', x, y, z))
            
            # Attribute byte count
            f.write(struct.pack('<H', 0))
    
    print(f"Written {len(faces)} triangles to {filename}")

def write_stl_ascii(vertices, faces, filename):
    """Write ASCII STL file"""
    with open(filename, 'w') as f:
        f.write("solid glTF_converted\n")
        
        for face in faces:
            # Calculate normal
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            u = v1 - v0
            v = v2 - v0
            normal = np.array([
                u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0]
            ])
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal = normal / norm
            
            f.write(f"facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
            f.write("  outer loop\n")
            
            for vertex_idx in face:
                x, y, z = vertices[vertex_idx]
                f.write(f"    vertex {x:.6f} {y:.6f} {z:.6f}\n")
            
            f.write("  endloop\n")
            f.write("endfacet\n")
        
        f.write("endsolid glTF_converted\n")
    
    print(f"Written ASCII STL with {len(faces)} faces to {filename}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python glb_to_stl.py input.glb output.stl [--ascii]")
        print("Example: python glb_to_stl.py model.glb model.stl")
        print("         python glb_to_stl.py model.glb model.stl --ascii")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    use_ascii = len(sys.argv) > 3 and sys.argv[3] == '--ascii'
    
    try:
        print(f"Parsing {input_file}...")
        scene, bin_data = parse_glb(input_file)
        
        print(f"Scene has {len(scene.get('meshes', []))} mesh(es)")
        
        vertices, faces = extract_mesh_from_glb(scene, bin_data)
        
        print(f"Extracted {len(vertices)} vertices, {len(faces)} faces")
        print(f"Vertex bounds: X({vertices[:,0].min():.3f} to {vertices[:,0].max():.3f})")
        print(f"              Y({vertices[:,1].min():.3f} to {vertices[:,1].max():.3f})")
        print(f"              Z({vertices[:,2].min():.3f} to {vertices[:,2].max():.3f})")
        
        if use_ascii:
            write_stl_ascii(vertices, faces, output_file)
        else:
            write_stl_binary(vertices, faces, output_file)
        
        print("Conversion successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: If glTF parsing fails, try simple extraction
        print("\nTrying fallback extraction...")
        simple_extraction(input_file, output_file)

def simple_extraction(input_file, output_file):
    """Fallback method for simpler extraction"""
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Look for vertex data patterns in the binary section
    # glTF binary section usually starts after JSON
    import re
    
    # Look for float patterns (common in vertex data)
    # This is a heuristic approach
    floats = struct.unpack('f' * (len(data) // 4), data[:len(data) - (len(data) % 4)])
    
    # Group into vertices (assuming they're consecutive floats)
    vertices = []
    for i in range(0, len(floats) - 2, 3):
        vertices.append([floats[i], floats[i+1], floats[i+2]])
    
    if len(vertices) < 3:
        print("Could not extract sufficient vertex data")
        return
    
    # Create simple faces (triangle fan)
    faces = []
    for i in range(1, len(vertices) - 1):
        faces.append([0, i, i+1])
    
    vertices = np.array(vertices[:100])  # Limit to first 100 vertices
    faces = np.array(faces[:98])  # Corresponding faces
    
    # Write STL
    with open(output_file, 'wb') as f:
        header = b'Simple extraction' + b'\x00' * 63
        f.write(header)
        f.write(struct.pack('<I', len(faces)))
        
        for face in faces:
            f.write(struct.pack('<fff', 0, 0, 0))  # Zero normal
            for idx in face:
                x, y, z = vertices[idx]
                f.write(struct.pack('<fff', x, y, z))
            f.write(struct.pack('<H', 0))
    
    print(f"Fallback: Wrote {len(faces)} faces to {output_file}")

if __name__ == "__main__":
    main()