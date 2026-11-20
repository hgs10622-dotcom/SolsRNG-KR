#!/usr/bin/env python3
"""Generate original, locally hosted AETHER RNG aura GLB assets."""
from pathlib import Path
import math
import numpy as np
import trimesh

OUT = Path("assets/aura")
OUT.mkdir(parents=True, exist_ok=True)

PALETTE = {
"dust":(0.72,0.84,1.0),"leaf":(0.38,0.92,0.55),"bubble":(0.28,0.86,1.0),
"ember":(1.0,0.31,0.08),"frost":(0.48,0.85,1.0),"tide":(0.08,0.55,1.0),
"storm":(0.45,0.62,1.0),"nebula":(0.66,0.35,1.0),"phantom":(0.55,0.48,0.95),
"solar":(1.0,0.55,0.08),"lunar":(0.65,0.75,1.0),"singularity":(0.95,0.2,0.55),
"chronos":(1.0,0.68,0.25),"aurora":(0.25,1.0,0.75),"eclipse":(0.48,0.25,0.95),
"seraph":(1.0,0.82,0.48),"infinity":(0.35,0.9,1.0),"origin":(1.0,0.48,0.18)
}
def mat(rgb, metallic=.55, rough=.24, glow=.25, alpha=1.0):
    c=[int(max(0,min(1,x))*255) for x in rgb]+[int(alpha*255)]
    return trimesh.visual.material.PBRMaterial(
        name="AETHER luminous alloy", baseColorFactor=c,
        metallicFactor=metallic, roughnessFactor=rough,
        emissiveFactor=[min(1,x*glow) for x in rgb])
def mesh_sphere(r, rgb, pos=(0,0,0), scale=(1,1,1), sub=3, metallic=.45, rough=.25, glow=.3):
    m=trimesh.creation.icosphere(subdivisions=sub, radius=r)
    m.apply_scale(scale); m.apply_translation(pos); m.visual.material=mat(rgb,metallic,rough,glow); return m
def cyl(a,b,r,rgb, sections=12, r2=None):
    a=np.array(a,float); b=np.array(b,float); d=b-a; length=np.linalg.norm(d)
    if length<1e-6: return mesh_sphere(r,rgb,a)
    m=trimesh.creation.cone(r, length, sections=sections) if r2 is None else trimesh.creation.cylinder(radius=r,height=length,sections=sections)
    # cylinder/cone initially along Z
    z=np.array([0.,0.,1.]); axis=d/length; cross=np.cross(z,axis); dot=np.clip(np.dot(z,axis),-1,1)
    if np.linalg.norm(cross)>1e-8: m.apply_transform(trimesh.geometry.align_vectors(z,axis))
    elif dot<0: m.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]))
    m.apply_translation((a+b)/2); m.visual.material=mat(rgb,.5,.25,.5); return m
def torus(R,r,rgb,axis=(0,0,1),segments=96,sides=12):
    verts=[]; faces=[]
    axis=np.array(axis,float); axis/=np.linalg.norm(axis)
    u=np.cross(axis,[0,1,0])
    if np.linalg.norm(u)<1e-5: u=np.cross(axis,[1,0,0])
    u/=np.linalg.norm(u); v=np.cross(axis,u)
    for i in range(segments):
        t=2*math.pi*i/segments; center=R*(math.cos(t)*u+math.sin(t)*v); radial=math.cos(t)*u+math.sin(t)*v
        for j in range(sides):
            q=2*math.pi*j/sides; p=center+r*(math.cos(q)*radial+math.sin(q)*axis); verts.append(p)
    for i in range(segments):
        for j in range(sides):
            a=i*sides+j; b=((i+1)%segments)*sides+j; c=((i+1)%segments)*sides+(j+1)%sides; d=i*sides+(j+1)%sides
            faces.extend([(a,b,d),(b,c,d)])
    m=trimesh.Trimesh(vertices=verts,faces=faces,process=False); m.visual.material=mat(rgb,.8,.16,.8); return m
def tube(points,r,rgb):
    pieces=[]
    for a,b in zip(points[:-1],points[1:]): pieces.append(cyl(a,b,r,rgb,10))
    return trimesh.util.concatenate(pieces)
def crystal(height,rgb,pos=(0,0,0),radius=.22):
    m=trimesh.creation.cone(radius,height,sections=6); m.apply_translation(pos); m.visual.material=mat(rgb,.72,.16,.8); return m
def leaf_mesh(rgb):
    # sculpted tapered leaf with raised central vein
    verts=[]; faces=[]; rows=32
    for i in range(rows+1):
        t=i/rows; w=.72*math.sin(math.pi*t)**.82
        for j in range(9):
            u=(j/8*2-1); verts.append([u*w, (t-.5)*2.8, .18*(1-u*u)*math.sin(math.pi*t)])
    for i in range(rows):
        for j in range(8):
            a=i*9+j; faces += [(a,a+9,a+1),(a+1,a+9,a+10)]
    m=trimesh.Trimesh(vertices=verts,faces=faces,process=False); m.visual.material=mat(rgb,.35,.3,.55)
    vein=tube([[0,-1.35,.08],[0,-.6,.2],[0,0,.19],[0,.7,.2],[0,1.35,.08]],.025,(.85,1,.85))
    return [m,vein]
def build(key,rgb):
    parts=[]
    add=parts.append
    if key=="dust":
        for i in range(15):
            a=i*2.399; rr=.35+(i%4)*.17
            add(mesh_sphere(.42,rgb,(math.cos(a)*rr,math.sin(a)*rr*.68,math.sin(i*1.7)*.24),(1,.78,.82),2,.12,.8,.2))
        for k in range(3): add(torus(.85+k*.22,.018,(.82,.92,1),(0.2,k*.35,1)))
    elif key=="leaf":
        for x,y,z,s in [(-.55,-.35,0,.72),(.48,.28,.15,.62),(.0,.85,-.1,.48)]:
            for p in leaf_mesh(rgb):
                p.apply_scale(s); p.apply_translation((x,y,z)); add(p)
        add(tube([[0,-1.25,0],[0,0,.1],[0,1.35,0]],.035,(.9,1,.85)))
    elif key=="bubble":
        for i in range(13):
            a=i*2.4; rr=.45+(i%4)*.2
            add(mesh_sphere(.22+(i%3)*.07,(.55,.94,1),(math.cos(a)*rr,math.sin(a)*rr,math.sin(i)*.35),(1,1,1),3,.08,.06,.65))
        add(torus(1.28,.025,(.55,.92,1),(1,.2,.3)))
    elif key=="ember":
        add(mesh_sphere(.58,(1,.22,.025),(0,-.35,0),(1,.8,.9),3,.2,.2,1))
        for i in range(9):
            a=i*2*math.pi/9; x=math.cos(a)*.42
            add(crystal(1.35+(i%3)*.25,(1,.22+.07*(i%2),.025),(x,.35,math.sin(a)*.28),.2))
        for i in range(5): add(torus(.7+i*.12,.025,(1,.55,.08),(i*.3,1,i*.2)))
    elif key=="frost":
        add(mesh_sphere(.48,(.78,.94,1),(0,0,0),sub=2,metallic=.7,rough=.12,glow=.7))
        for i in range(10):
            a=i*2*math.pi/10; x=math.cos(a)*.72; z=math.sin(a)*.72
            c=crystal(1.25+(i%3)*.42,(.55,.88,1),(x,.0,z),.23)
            c.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0])); add(c)
        add(torus(1.45,.018,(.8,.97,1),(1,.3,.2)))
    elif key=="tide":
        add(mesh_sphere(.62,(.04,.28,.78),(0,0,0),(1.2,.8,1),3,.65,.12,.6))
        for i in range(7): add(torus(.55+i*.16,.045,(.12,.72,1),(1,.15,i*.18)))
        for i in range(8):
            a=i*math.pi/4; add(mesh_sphere(.11,(.4,.9,1),(math.cos(a)*1.25,.12,math.sin(a)*1.25),sub=2))
    elif key=="storm":
        add(mesh_sphere(.42,(.5,.68,1),(0,0,0),sub=2,metallic=.8,rough=.12,glow=1))
        for i in range(7):
            a=i*2*math.pi/7; pts=[]
            for j in range(6):
                rr=.2+j*.22; ang=a+(j%2-.5)*.48
                pts.append((math.cos(ang)*rr,math.sin(ang)*rr,math.sin(j*3+i)*.18))
            add(tube(pts,.045,(.62,.78,1)))
    elif key=="nebula":
        add(mesh_sphere(.4,(.22,.04,.55),(0,0,0),sub=3,glow=.8))
        for arm in range(5):
            pts=[]
            for j in range(100):
                t=j/99; a=t*math.pi*3+arm*2*math.pi/5; rr=.12+1.48*t
                pts.append((math.cos(a)*rr,math.sin(a)*rr,.18*math.sin(t*18+arm)))
            add(tube(pts,.035,(.9,.38,.95) if arm%2 else rgb))
        for i in range(35):
            a=i*2.4; rr=.5+(i%9)*.15; add(mesh_sphere(.035,(.8,.75,1),(math.cos(a)*rr,math.sin(a)*rr,.3*math.sin(i)),sub=1))
    elif key=="phantom":
        add(mesh_sphere(.78,(.42,.34,.82),(0,.1,0),(1,1.3,.62),3,.25,.12,.7))
        add(mesh_sphere(.38,(.04,.025,.12),(0,.25,.48),sub=2,glow=.05))
        for x in [-.22,.22]: add(mesh_sphere(.07,(.75,.9,1),(x,.32,.79),sub=2,glow=1))
        for i in range(7):
            a=i*2*math.pi/7; add(tube([[math.cos(a)*.45,-.55,0],[math.cos(a)*.7,-1.0,.05],[math.cos(a)*.8,-1.5,.12]],.045,(.62,.56,1)))
    elif key=="solar":
        add(mesh_sphere(.88,(1,.48,.035),(0,0,0),sub=4,metallic=.2,rough=.4,glow=1))
        for i in range(32):
            a=i*2*math.pi/32; add(crystal(.55+(i%4)*.13,(1,.58,.12),(math.cos(a)*1.18,math.sin(a)*1.18,0),.12))
        for i in range(3): add(torus(1.35+i*.16,.018,(1,.82,.35),(i*.5,.3+i*.4,.2)))
    elif key=="lunar":
        add(mesh_sphere(1.0,(.66,.75,.92),(0,0,0),sub=4,metallic=.25,rough=.72,glow=.12))
        for i in range(15):
            a=i*2.399; rr=.45+(i%4)*.13
            add(mesh_sphere(.09+(i%3)*.035,(.34,.43,.62),(math.cos(a)*rr,math.sin(a)*rr,.86),scale=(1,1,.18),sub=2,metallic=.1,rough=.95,glow=.03))
        add(torus(1.3,.018,(.72,.83,1),(1.1,.2,.3)))
    elif key=="singularity":
        add(mesh_sphere(.62,(.005,.002,.018),(0,0,0),sub=4,metallic=1,rough=.04,glow=.02))
        for i in range(9): add(torus(.78+i*.085,.035,(1,.16,.48) if i%2 else (1,.72,.9),(.2+i*.11,.3,i*.16)))
        add(tube([(-2,0,0),(-1.2,0,0),(0,0,0),(1.2,0,0),(2,0,0)],.07,(1,.5,.82)))
    elif key=="chronos":
        add(cyl((0,0,-.16),(0,0,.16),1.0,(.12,.07,.025),96))
        add(torus(1.05,.075,(1,.67,.24)))
        add(torus(.88,.018,(1,.9,.62)))
        for i in range(12):
            a=i*math.pi/6; add(cyl((math.sin(a)*.78,math.cos(a)*.78,.2),(math.sin(a)*.9,math.cos(a)*.9,.2),.025,(1,.83,.48),8))
        add(cyl((0,0,.24),(0,.57,.24),.035,(1,.92,.7),10)); add(cyl((0,0,.25),(.48,-.28,.25),.028,(1,.68,.24),10))
        add(mesh_sphere(.09,(1,.85,.5),(0,0,.28),sub=2))
    elif key=="aurora":
        for band in range(11):
            pts=[]
            for j in range(65):
                t=j/64; x=-1.6+3.2*t; y=.8-band*.16+math.sin(t*8+band*.55)*(.16+band*.008); z=math.cos(t*6+band)*.18
                pts.append((x,y,z))
            add(tube(pts,.035+band*.002,((.18,.95,.72) if band%2 else (.38,.65,1))))
        for i in range(20):
            a=i*2.4; add(mesh_sphere(.035,(.7,1,.88),(math.cos(a)*1.5,math.sin(a)*1.2,.2),sub=1))
    elif key=="eclipse":
        add(mesh_sphere(.88,(.012,.008,.04),(0,0,0),sub=4,metallic=.9,rough=.08,glow=.04))
        add(torus(1.12,.09,(.52,.22,1),(.25,.1,.05))); add(torus(1.3,.022,(.9,.8,1),(.6,.3,.2)))
        for i in range(36):
            a=i*2*math.pi/36; add(cyl((math.cos(a)*1.32,math.sin(a)*1.32,0),(math.cos(a)*1.52,math.sin(a)*1.52,0),.025,(.7,.48,1),6))
    elif key=="seraph":
        add(mesh_sphere(.24,(1,.82,.52),(0,-.18,0),scale=(.8,1.7,.7),sub=3))
        for side in [-1,1]:
            for row in range(5):
                for j in range(9-row):
                    x=side*(.32+j*.13-row*.05); y=.05+row*.22+j*.035
                    f=crystal(.75-row*.065,(1,.82,.52) if row%2 else (1,.95,.78),(x,y,-.12),.085)
                    f.apply_transform(trimesh.transformations.rotation_matrix(side*(-.5+j*.08),[0,0,1])); add(f)
        add(torus(.48,.035,(1,.75,.32),(1.2,0,0)))
    elif key=="infinity":
        # triple intertwined torus-knot-like loops
        for k in range(3):
            pts=[]
            for j in range(260):
                t=j/259*math.pi*2; x=1.0*math.sin(2*t+k*2.094); y=.72*math.sin(3*t); z=.45*math.cos(2*t+k*2.094)
                pts.append((x,y,z))
            add(tube(pts,.055,[(.2,.9,1),(1,.35,.82),(.92,.95,1)][k]))
        add(torus(1.5,.016,(.7,1,1),(.7,.3,.2)))
    elif key=="origin":
        add(mesh_sphere(.68,(1,.42,.12),(0,0,0),sub=3,metallic=.8,rough=.18,glow=.9))
        for i in range(8):
            a=i*math.pi/4; add(crystal(1.25,(1,.62,.2),(math.cos(a)*.55,math.sin(a)*.55,.1),.2))
        # angular crown and sweeping tail
        add(tube([(-.25,.1,0),(-.85,.55,.15),(-1.15,.95,.1),(-.55,1.1,.2),(0,.85,.1),(.65,1.15,0),(1.05,.85,-.1)],.065,(1,.75,.3)))
        add(torus(1.55,.022,(1,.72,.35),(.4,.8,.2)))

    # High-tier signature architecture: a complete astral gate, not just a glow.
    # Separate machined rings, radial braces, crown spires and engraved markers
    # give the silhouette depth when viewed from the front or at an angle.
    if key in {"nebula","phantom","solar","lunar","singularity","chronos","aurora","eclipse","seraph","infinity","origin"}:
        accent = tuple(min(1.0, c*0.72+0.22) for c in rgb)
        pale = tuple(min(1.0, c*0.38+0.58) for c in rgb)
        dark = tuple(c*0.20 for c in rgb)
        # Three independently tilted precision rings.
        add(torus(1.48,.045,rgb,(0.12,.08,1),144,14))
        add(torus(1.68,.022,pale,(.62,.18,.76),144,10))
        add(torus(1.88,.032,accent,(-.38,.72,.58),160,12))
        # Inner segmented ring and small inset nodes.
        for i in range(32):
            a=2*math.pi*i/32
            x,y=1.55*math.cos(a),1.55*math.sin(a)
            add(cyl((x*.94,y*.94,.02),(x*1.035,y*1.035,.02),.026,pale,8))
            if i%2==0:
                add(mesh_sphere(.043,accent,(1.72*math.cos(a),1.72*math.sin(a),.035),sub=2,metallic=.9,rough=.12,glow=.9))
        # Eight substantial structural pylons around the gate.
        for i in range(8):
            a=2*math.pi*i/8 + math.pi/8
            ca,sa=math.cos(a),math.sin(a)
            base=(1.26*ca,1.26*sa,-.16)
            tip=(1.93*ca,1.93*sa,.12*math.sin(a*2))
            add(cyl(base,tip,.075,accent,12))
            add(mesh_sphere(.105,pale,tip,sub=2,metallic=.85,rough=.14,glow=.8))
            # Faceted crown crystal on alternating pylons.
            if i%2==0:
                shard=crystal(.48,rgb,(1.98*ca,1.98*sa,.18),.115)
                shard.apply_transform(trimesh.transformations.rotation_matrix(a,[0,0,1]))
                add(shard)
        # Floating rune plates, each with a bright central inlay.
        for i in range(16):
            a=2*math.pi*i/16
            x,y=1.78*math.cos(a),1.78*math.sin(a)
            plate=trimesh.creation.box(extents=(.18,.075,.045))
            plate.apply_transform(trimesh.transformations.rotation_matrix(a,[0,0,1]))
            plate.apply_translation((x,y,.10))
            plate.visual.material=mat(dark,.92,.2,.18)
            add(plate)
            add(cyl((x,y,.13),(x+.035*math.cos(a),y+.035*math.sin(a),.13),.012,pale,6))
        # Four long energy vanes create a readable star-shaped silhouette.
        for i in range(4):
            a=math.pi/4+i*math.pi/2
            ca,sa=math.cos(a),math.sin(a)
            add(tube([
                (.32*ca,.32*sa,.12),
                (.82*ca,.82*sa,.22),
                (1.38*ca,1.38*sa,.08),
                (1.92*ca,1.92*sa,-.08)],.027,pale))
            add(mesh_sphere(.075,rgb,(1.40*ca,1.40*sa,.08),sub=2,metallic=.8,rough=.12,glow=1))
        # A small, layered crown above the core.
        for side in (-1,1):
            x=side*.30
            add(tube([[x,-.25,.2],[x*1.55,.22,.22],[x*1.75,.72,.16],[x*1.15,1.12,.08]],.038,accent))
            add(crystal(.42,pale,(x*1.75,.78,.16),.095))
        # Central floating halo and a fine orbiting bead constellation.
        add(torus(.78,.018,pale,(.18,.24,1),128,8))
        for i in range(12):
            a=2*math.pi*i/12
            add(mesh_sphere(.032,pale,(.92*math.cos(a),.92*math.sin(a),.30*math.sin(2*a)),sub=2,metallic=.75,rough=.1,glow=1))
        # Tier-specific signature additions.
        if key in {"singularity","eclipse"}:
            add(torus(1.12,.075,(1.0,.24,.62),(.22,.62,.75),160,18))
            for i in range(6):
                a=i*math.pi/3
                add(tube([[.42*math.cos(a),.42*math.sin(a),.25],[.9*math.cos(a+.3),.9*math.sin(a+.3),.08],[1.5*math.cos(a),1.5*math.sin(a),-.12]],.035,pale))
        elif key in {"chronos","infinity"}:
            for i in range(12):
                a=i*math.pi/6
                add(cyl((1.15*math.cos(a),1.15*math.sin(a),.22),(1.38*math.cos(a),1.38*math.sin(a),.22),.035,pale,10))
        elif key in {"seraph","origin"}:
            for side in (-1,1):
                for row in range(3):
                    y=.18+row*.22
                    add(tube([[side*.28,y,.12],[side*(.72+row*.12),y+.32,.06],[side*(1.18+row*.12),y+.58,-.02]],.045,pale))
    return parts

for key,rgb in PALETTE.items():
    scene=trimesh.Scene()
    for i,m in enumerate(build(key,rgb)):
        scene.add_geometry(m,geom_name=f"{key}_mesh_{i:03d}",node_name=f"{key}_part_{i:03d}")
    # Normalize all source geometry around origin with consistent framing.
    bounds=scene.bounds
    center=(bounds[0]+bounds[1])/2
    extent=max(bounds[1]-bounds[0])
    scale=2.65/(extent or 1)
    transform=np.eye(4); transform[:3,:3]*=scale; transform[:3,3]=-center*scale
    scene.apply_transform(transform)
    scene.export(OUT/f"{key}.glb")
    print("generated",key,(OUT/f"{key}.glb").stat().st_size)
