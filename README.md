# simple_glb_2_stl_converter  - Quick & Dirty GLB to STL Converter
Simple converstion from glb to stl, had to craft a conversion for meta's segment anything ai model


A no-bs, one-job command line tool to convert `.glb` (or `.gbl`) 3D files to `.stl` format. Works when you just need it done, not perfect.  I just downloaded a glb format file from metas new segment anything tool and wanted to print the model.

## What It Is

This is a **single Python script** that converts GLTF binary files to STL format. It's:
- **Simple** - One file, no dependencies beyond Python standard library
- **Fast** - Gets the job done in seconds
- **Dirty** - Makes assumptions that work for most cases
- **No-frills** - Does exactly one thing: GLB → STL

## What It Isn't

- **Not a full glTF parser** - Doesn't handle materials, textures, animations, or complex scenes
- **Not production-ready** - No error recovery, minimal validation
- **Not a 3D editor** - Just converts mesh data

## Quick Start

```bash
# Clone or download just the script
git clone git@github.com:BuckRogers1965/simple_glb_2_stl_converter.git


# Convert a file
python glb_to_stl.py model.glb output.stl

# Or use ASCII STL (easier to debug)
python glb_to_stl.py model.glb output.stl --ascii
```

That's it. No installation, no setup, no bullshit.

## How It Works

1. **Parses** the glTF binary format (magic number: `glTF`)
2. **Extracts** vertex and face data from the binary chunk
3. **Converts** to STL (triangle mesh format)
4. **Writes** the result

## Limitations

### It Assumes:
- Your GLB file contains exactly one mesh
- The mesh uses triangle faces (not lines or points)
- You want all geometry converted (no filtering)
- Standard glTF layout (JSON chunk then BIN chunk)

### It Ignores:
- Textures and materials (STL doesn't support them anyway)
- Animations
- Multiple meshes or scenes
- Complex node hierarchies
- UV coordinates and vertex colors

### It Might Break On:
- Compressed glTF (.gltf + .bin separate files)
- Draco compression
- Instanced geometry
- Non-standard buffer layouts

## When To Use This

✅ **Use this when:**
- You just exported a 3D model as GLB and need STL for 3D printing
- You're in a hurry and need a quick conversion
- Your GLB file is simple (single mesh, no fancy features)
- You don't care about materials or textures

❌ **Don't use this when:**
- You need perfect preservation of scene hierarchy
- You have complex materials/textures
- You're processing production assets
- You need validation or error reporting

## Examples

```bash
# Basic conversion
python glb_to_stl.py sculpture.glb sculpture.stl

# ASCII output (human-readable)
python glb_to_stl.py robot.glb robot.stl --ascii

# Batch conversion (use with find/xargs)
find . -name "*.glb" -exec sh -c 'python glb_to_stl.py "$1" "${1%.glb}.stl"' _ {} \;
```

## What's In The Box

```
glb_to_stl.py      # The only file you need
```

No config files, no dependencies, no installation scripts. Just one Python file.

## Troubleshooting

### "Not a valid glTF binary file"
Your file might be:
- Text-based glTF (.gltf) instead of binary (.glb)
- Corrupted or truncated
- Actually a different format (FBX, OBJ, etc.)

**Fix:** Use a proper 3D editor to export as binary glTF (.glb)

### Output STL is empty or tiny
The script might be reading wrong buffer offsets.

**Fix:** Try the `--ascii` flag first to see what's being exported. If it's wrong, your GLB file might have non-standard layout.

### "Error: Expected JSON chunk first"
Your GLB file might have chunks in unexpected order.

**Fix:** This script assumes standard glTF layout. You might need a full glTF parser.

## Why This Exists

Because sometimes you just need to convert a fucking file without:
- Installing Blender
- Learning a new UI
- Dealing with 500 MB software packages
- Creating accounts
- Reading documentation

This gets you from GLB to STL in under 30 seconds. That's it.

## License

MIT - Do whatever you want with it. If it breaks, you get to keep both pieces.

## Contributing

Don't. This is a quick & dirty tool. If you need features, use:
- [Blender](https://www.blender.org/) (full-featured, free)
- [MeshLab](http://www.meshlab.net/) (open source mesh processing)
- [Assimp](https://github.com/assimp/assimp) (library for proper conversion)

This script exists for the 80% case where you just need it done now.

---

**Remember:** This is the duct tape of 3D format conversion. It's ugly, it's temporary, but it works when you're in a pinch.
