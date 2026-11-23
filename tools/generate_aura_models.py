#!/usr/bin/env python3
"""Generate original, locally hosted AETHER RNG aura GLB assets."""
from pathlib import Path
import math, json, colorsys
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


def css_rgb(value):
    value=str(value).strip()
    if value.startswith("#"):
        h=value.lstrip("#")
        return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
    if value.startswith("hsl("):
        import re
        nums=[float(x) for x in re.findall(r"[-+]?\d*\.?\d+",value)]
        h,s,l=nums[0]%360/360,nums[1]/100,nums[2]/100
        return colorsys.hls_to_rgb(h,l,s)
    return (0.55,0.72,1.0)

def archetype_parts(archetype, rgb, seed, tier):
    """Compact, polished archetype core; per-ID geometry is added separately."""
    rng=np.random.default_rng(seed ^ 0x5A17)
    parts=[]
    accent=tuple(min(1,c*.62+.30) for c in rgb)
    pale=tuple(min(1,c*.22+.72) for c in rgb)
    if archetype=="dust":
        for i in range(7):
            a=i*2.399; r=.24+(i%3)*.19
            parts.append(mesh_sphere(.19+(i%2)*.06,rgb,(math.cos(a)*r,math.sin(a)*r,.16*math.sin(i)),sub=2,metallic=.25,rough=.55,glow=.35))
    elif archetype=="ember":
        parts.append(mesh_sphere(.52,rgb,(0,0,0),sub=3,metallic=.35,rough=.2,glow=.9))
        for i in range(7):
            a=i*math.tau/7
            parts.append(crystal(.85+(i%3)*.2,accent,(.62*math.cos(a),.62*math.sin(a),.04),.14))
    elif archetype=="tide":
        parts.append(mesh_sphere(.56,rgb,(0,0,0),(1.1,.72,.9),sub=3,metallic=.7,rough=.12,glow=.7))
        for i in range(3):
            parts.append(torus(.78+i*.22,.035,accent,(.25+i*.45,.4-i*.22,.2),72,10))
    elif archetype=="nebula":
        parts.append(mesh_sphere(.36,tuple(c*.4 for c in rgb),(0,0,0),sub=3,metallic=.3,rough=.25,glow=.9))
        for arm in range(3):
            pts=[]
            for j in range(65):
                q=j/64; a=q*math.tau*2+arm*math.tau/3; rad=.15+1.15*q
                pts.append((math.cos(a)*rad,math.sin(a)*rad,.14*math.sin(q*15+arm)))
            parts.append(tube(pts,.027,accent if arm%2 else pale))
    elif archetype=="solar":
        parts.append(mesh_sphere(.62,rgb,(0,0,0),sub=3,metallic=.3,rough=.28,glow=1))
        for i in range(12):
            a=i*math.tau/12
            parts.append(crystal(.5+(i%3)*.16,accent,(1.02*math.cos(a),1.02*math.sin(a),0),.085))
    elif archetype=="singularity":
        parts.append(mesh_sphere(.5,tuple(c*.13 for c in rgb),(0,0,0),sub=3,metallic=1,rough=.035,glow=.03))
        for i in range(4):
            parts.append(torus(.72+i*.16,.035,accent if i%2 else pale,(i*.38,.35+i*.19,.2),72,10))
    elif archetype=="aurora":
        for band in range(5):
            pts=[]
            for j in range(48):
                q=j/47; x=-1.25+2.5*q
                y=.5-band*.2+math.sin(q*8+band*.7)*.18
                z=.18*math.cos(q*6+band)
                pts.append((x,y,z))
            parts.append(tube(pts,.026+band*.002,accent if band%2 else pale))
    else:
        parts.append(mesh_sphere(.42,rgb,(0,0,0),sub=3,metallic=.8,rough=.16,glow=.9))
        for i in range(8):
            a=i*math.tau/8
            parts.append(crystal(1.0+(i%3)*.2,accent,(.58*math.cos(a),.58*math.sin(a),.08),.15))
    return parts

def unique_parts(aura, seed):
    """Deterministic per-aura sculptural additions; each ID gets its own silhouette."""
    rng=np.random.default_rng(seed)
    rgb=css_rgb(aura.get("color","#8bdcff"))
    tier=int(aura.get("tier",0))
    parts=[]
    accent=tuple(min(1,c*.55+.38) for c in rgb)
    pale=tuple(min(1,c*.25+.68) for c in rgb)
    dark=tuple(c*.18 for c in rgb)

    # A unique central form, selected from several genuinely different solids.
    shape=seed%7
    if shape==0:
        core=trimesh.creation.icosphere(subdivisions=2+(seed%2),radius=.42+rng.random()*.22)
        core.apply_scale([.72+rng.random()*.7,.75+rng.random()*.9,.72+rng.random()*.7])
    elif shape==1:
        core=trimesh.creation.cone(.48+rng.random()*.2,1.0+rng.random()*.8,sections=5+seed%5)
        core.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    elif shape==2:
        core=trimesh.creation.cylinder(radius=.35+rng.random()*.22,height=1.0+rng.random()*.8,sections=7+seed%8)
    elif shape==3:
        core=trimesh.creation.icosphere(subdivisions=1,radius=.65)
        core.apply_scale([1.3,.55,.72])
    elif shape==4:
        core=trimesh.creation.box(extents=[.7+rng.random()*.45,.7+rng.random()*.45,.7+rng.random()*.45])
        core.apply_transform(trimesh.transformations.rotation_matrix(rng.random()*math.pi,[1,1,1]))
    elif shape==5:
        core=trimesh.creation.torus(major_radius=.48,minor_radius=.14)
    else:
        core=trimesh.creation.icosphere(subdivisions=2,radius=.5)
        core.apply_scale([.52,1.45,.58])
    core.visual.material=mat(rgb,.82,.16,.9)
    parts.append(core)

    # Unequal orbital architecture: deliberately asymmetric and seed-specific.
    ring_count=1+seed%4+tier//3
    for i in range(ring_count):
        radius=.72+float(rng.random())*1.0
        axis=rng.normal(size=3)
        parts.append(torus(radius,.012+float(rng.random())*.026,
                           accent if i%2==0 else pale,axis,
                           segments=64+int(rng.integers(0,64)),sides=8+int(rng.integers(0,5))))
    # Different numbers, angles, and lengths of sculpted crystal fins.
    spike_count=3+seed%8+tier
    for i in range(spike_count):
        angle=2*math.pi*i/spike_count+float(rng.uniform(-.22,.22))
        radius=.72+float(rng.random())*.5
        height=.48+float(rng.random())*(.55+tier*.16)
        pos=(math.cos(angle)*radius,float(rng.uniform(-.35,.45)),math.sin(angle)*radius)
        shard=crystal(height,accent if i%3 else pale,pos,.075+float(rng.random())*.12)
        shard.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,1,0]))
        parts.append(shard)
    # One to three individually wound energy filaments.
    for strand in range(1+seed%3):
        turns=1.2+float(rng.random())*3.8
        pts=[]
        phase=float(rng.uniform(0,math.pi*2))
        for j in range(100):
            q=j/99
            ang=q*turns*math.pi*2+phase
            rad=.42+q*(.72+float(rng.random())*.05)
            pts.append((math.cos(ang)*rad,
                        (q-.5)*(.9+tier*.08),
                        math.sin(ang)*rad))
        parts.append(tube(pts,.012+float(rng.random())*.018,accent))
    # Signature floating satellites, placed on non-coplanar trajectories.
    for i in range(5+seed%12+tier*2):
        ang=float(rng.uniform(0,math.pi*2))
        rad=float(rng.uniform(1.15,2.15))
        pos=(math.cos(ang)*rad,float(rng.uniform(-1.45,1.45)),math.sin(ang)*rad)
        r=float(rng.uniform(.035,.12))
        node=mesh_sphere(r,pale,pos,sub=1+int(rng.integers(0,2)),metallic=.9,rough=.12,glow=1)
        parts.append(node)
    # A tier-specific crown / wing silhouette, not just more particles.
    if tier>=3:
        wing_count=2+(seed%3)
        for side in (-1,1):
            for w in range(wing_count):
                x=side*(.38+w*.17)
                y=.25+w*.18
                pts=[(x,y,0),(x+side*.35,y+.34,.08),(x+side*(.62+w*.12),y+.72,.02),(x+side*.34,y+1.0,-.08)]
                parts.append(tube(pts,.035+ tier*.003, pale if w%2 else accent))
    return parts

catalog_path=Path("supabase/aura_catalog.json")
if not catalog_path.exists():
    raise SystemExit("supabase/aura_catalog.json is required to build unique aura assets")
catalog=json.loads(catalog_path.read_text(encoding="utf-8"))
if len(catalog)!=1000 or len({a["id"] for a in catalog})!=1000:
    raise SystemExit("Aura catalog must contain exactly 1,000 unique IDs")

for index,aura in enumerate(catalog):
    aura_id=aura["id"]
    archetype=aura.get("model_id","origin")
    if archetype not in PALETTE:
        raise SystemExit(f"Unknown base model {archetype} for {aura_id}")
    seed=int.from_bytes(aura_id.encode("utf-8"),"little") % (2**32-1)
    rgb=css_rgb(aura.get("color","#8bdcff"))
    scene=trimesh.Scene()
    source_parts=archetype_parts(archetype,rgb,seed,int(aura.get("tier",0)))
    additions=unique_parts(aura,seed)
    for i,m in enumerate(source_parts+additions):
        # Preserve the original geometry/material architecture, but tint each
        # individual asset with its own palette and per-part metallic response.
        if hasattr(m,"visual"):
            shade=0.82+((seed+i*37)%19)/100
            part_rgb=tuple(min(1.0,c*shade) for c in rgb)
            m.visual.material=mat(part_rgb,.48+((seed+i)%45)/100,.12+((seed+i*3)%35)/100,.55+((seed+i*7)%35)/100)
        scene.add_geometry(m,geom_name=f"{aura_id}_mesh_{i:03d}",node_name=f"{aura_id}_part_{i:03d}")
    bounds=scene.bounds
    center=(bounds[0]+bounds[1])/2
    extent=max(bounds[1]-bounds[0])
    scale=2.65/(extent or 1)
    transform=np.eye(4); transform[:3,:3]*=scale; transform[:3,3]=-center*scale
    scene.apply_transform(transform)
    out=OUT/f"{aura_id}.glb"
    scene.export(out)
    if index%50==0 or index==len(catalog)-1:
        print(f"generated {index+1}/{len(catalog)}: {aura_id} ({out.stat().st_size} bytes)")
