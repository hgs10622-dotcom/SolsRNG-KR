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



def signature_parts(aura, seed):
    """Give each aura one of ten readable, silhouette-defining sculptural motifs."""
    rng=np.random.default_rng(seed ^ 0xA37E91)
    rgb=css_rgb(aura.get("color","#8bdcff"))
    accent=tuple(min(1,c*.58+.34) for c in rgb)
    pale=tuple(min(1,c*.22+.70) for c in rgb)
    dark=tuple(c*.24 for c in rgb)
    family=seed%10
    parts=[]
    if family==0:  # blooming crown
        for i in range(8):
            a=math.tau*i/8
            x,z=math.cos(a),math.sin(a)
            petal=mesh_sphere(.46,accent,(x*.78,.18,z*.78),(.42,1.55,.22),3,.62,.2,.85)
            petal.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0]))
            parts.append(petal)
            parts.append(crystal(.62,pale,(x*1.18,.68,z*1.18),.13))
    elif family==1:  # twin comet wings
        for side in (-1,1):
            for band in range(3):
                pts=[]
                for j in range(36):
                    q=j/35
                    pts.append((side*(.18+1.65*q),.45+band*.15+math.sin(q*math.pi*1.4+band*.5)*(.18+q*.25),-.2+band*.18+q*.24))
                parts.append(tube(pts,.025+band*.009,accent if band%2 else pale))
            parts.append(crystal(.9,pale,(side*1.55,.62,.12),.16))
    elif family==2:  # gyroscopic engine
        for axis in ((1,0,0),(0,1,0),(0,0,1)):
            parts.append(torus(1.02,.045,accent,axis,112,12))
        for i in range(6):
            a=math.tau*i/6
            p=(1.0*math.cos(a),1.0*math.sin(a),.32*math.sin(2*a))
            parts.append(mesh_sphere(.11,pale,p,sub=2,metallic=.95,rough=.1,glow=1))
    elif family==3:  # crystal spire cluster
        for i in range(11):
            a=math.tau*i/11
            r=.35+float(rng.random())*.65
            h=.65+float(rng.random())*1.35
            p=(math.cos(a)*r,float(rng.uniform(-.2,.25)),math.sin(a)*r)
            shard=crystal(h,accent if i%3 else pale,p,.11+float(rng.random())*.13)
            shard.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0]))
            parts.append(shard)
        parts.append(mesh_sphere(.3,dark,(0,0,0),sub=3,metallic=1,rough=.08,glow=.15))
    elif family==4:  # flowing spiral stream
        for strand in range(4):
            pts=[]
            phase=strand*math.tau/4
            for j in range(100):
                q=j/99
                a=q*math.tau*2.4+phase
                r=.3+q*1.15
                pts.append((math.cos(a)*r,(q-.5)*2.4,math.sin(a)*r))
            parts.append(tube(pts,.025+strand*.006,accent if strand%2 else pale))
    elif family==5:  # radial starburst
        for i in range(16):
            a=math.tau*i/16
            r=.82 if i%2 else 1.08
            start=(math.cos(a)*.36,0,math.sin(a)*.36)
            end=(math.cos(a)*r,.12*math.sin(3*a),math.sin(a)*r)
            parts.append(cyl(start,end,.035 if i%2 else .055,accent if i%3 else pale,8))
            if i%2==0: parts.append(mesh_sphere(.085,pale,end,sub=2,metallic=.9,rough=.12,glow=1))
    elif family==6:  # faceted containment cage
        verts=[]
        for y in (-.95,.95):
            for i in range(6):
                a=math.tau*i/6
                verts.append((math.cos(a),y,math.sin(a)))
        for i in range(6):
            a=math.tau*i/6
            parts.append(cyl(verts[i],verts[(i+1)%6],.035,accent,8))
            parts.append(cyl(verts[i+6],verts[((i+1)%6)+6],.035,pale,8))
            parts.append(cyl(verts[i],verts[i+6],.025,accent,8))
            if i%2==0: parts.append(crystal(.5,pale,verts[i],.09))
    elif family==7:  # orbiting moonlets
        for i in range(5):
            a=math.tau*i/5
            axis=(math.cos(a),.35*math.sin(a*2),math.sin(a))
            parts.append(torus(.78+i*.12,.025,accent if i%2 else pale,axis,96,10))
            p=(1.25*math.cos(a),.35*math.sin(a*2),1.25*math.sin(a))
            parts.append(mesh_sphere(.16+(i%2)*.06,pale,p,sub=3,metallic=.8,rough=.12,glow=.8))
    elif family==8:  # layered floating halo plates
        for i in range(7):
            a=math.tau*i/7
            plate=trimesh.creation.box(extents=(.48,.09,.3))
            plate.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0]))
            plate.apply_translation((1.0*math.cos(a),.28*math.sin(a*2),1.0*math.sin(a)))
            plate.visual.material=mat(accent if i%2 else pale,.86,.18,.75)
            parts.append(plate)
        parts.append(torus(1.35,.04,pale,(.25,.8,.4),128,12))
    else:  # split crown with a vertical energy column
        parts.append(cyl((0,-1.25,0),(0,1.25,0),.065,pale,12))
        for side in (-1,1):
            for i in range(4):
                x=side*(.35+i*.2)
                parts.append(tube([[0,.25,0],[x,.55+i*.1,.08],[side*(1.05+i*.13),1.0+i*.12,0]],.045,accent))
                parts.append(crystal(.48+i*.12,pale,(side*(.95+i*.14),1.02+i*.12,0),.10))
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


def themed_parts(aura, seed):
    """Build a name-led, tier-aware sculptural identity for one catalog entry."""
    rng=np.random.default_rng(seed)
    name=aura.get("name","")
    desc=aura.get("description","")
    tier=int(aura.get("tier",0))
    rgb=css_rgb(aura.get("color","#8bdcff"))
    accent=tuple(min(1,c*.58+.36) for c in rgb)
    pale=tuple(min(1,c*.24+.72) for c in rgb)
    deep=tuple(c*.20 for c in rgb)
    parts=[]
    def add(x): parts.append(x)
    def point(radius, angle, y=0):
        return (math.cos(angle)*radius,y,math.sin(angle)*radius)

    # Noun-driven silhouettes: each family has its own primary geometry.
    families=[
      (("물방울","구슬","유리구슬","보석","핵","핵심"),"prism"),
      (("별가루","별","성운","은하","우주","별빛"),"cosmos"),
      (("나뭇잎","새싹","꽃잎","꽃씨","꽃불","꽃"),"flora"),
      (("조약돌","모래알","파편","암석","바위","대지"),"geode"),
      (("물결","해류","소용돌이","파도","심해","폭풍","천둥"),"vortex"),
      (("깃털","천둥새","새","날개"),"wings"),
      (("구름","숨결","안개","영혼"),"mist"),
      (("반딧불","불씨","화염","불꽃","태양","꽃불"),"flame"),
      (("눈송이","서리","얼음","빙하","수정"),"frost"),
      (("달팽이","나선","시간","시계","크로노스"),"spiral"),
      (("성역","성당","수정궁","천궁","궁전","신전"),"sanctum"),
      (("창세문","문","차원","차원핵","차원문","관문"),"gate"),
      (("왕관","왕좌","군주","세라프","천사"),"crown"),
      (("혜성","유성","혜성핵","궤도"),"comet"),
      (("검","창","칼날","창조"),"blade"),
    ]
    family="relic"
    for words,key in families:
        if any(w in name for w in words):
            family=key
            break
    # adjective/prefix gives a second independent design influence
    mood=" ".join(name.split()[:2])
    phase=(seed%17)/17*math.tau
    scale=.82+(seed%9)*.055
    n=5+(seed%5)
    if family=="prism":
        add(mesh_sphere(.48,rgb,(0,0,0),scale=(.78,1.18,.78),sub=4,metallic=.82,rough=.10,glow=.85))
        for i in range(5):
            a=phase+i*math.tau/5
            c=crystal(1.05+(i%3)*.28,accent,point(.72,a,.12*math.sin(a)),.19)
            c.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0])); add(c)
        add(torus(.92,.035,pale,(.3,.8,.2),96,12))
    elif family=="cosmos":
        add(mesh_sphere(.38,deep,(0,0,0),sub=3,metallic=.9,rough=.06,glow=.35))
        for arm in range(3+seed%3):
            pts=[]
            for j in range(90):
                q=j/89; a=phase+arm*math.tau/(3+seed%3)+q*math.tau*2.1
                r=.12+1.45*q
                pts.append((math.cos(a)*r, .18*math.sin(q*18+arm), math.sin(a)*r))
            add(tube(pts,.025+(tier*.003),accent if arm%2 else pale))
        for i in range(18+tier*3):
            a=phase+i*2.399; r=.45+(i%7)*.19
            add(mesh_sphere(.025+(i%3)*.012,pale,point(r,a,.3*math.sin(i)),sub=2,metallic=.7,rough=.12,glow=1))
    elif family=="flora":
        for i in range(5+(seed%4)):
            a=phase+i*math.tau/(5+(seed%4))
            petal=mesh_sphere(.34,accent,point(.42,a,.12),(.42,1.35,.20),3,.55,.22,.7)
            petal.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0])); add(petal)
            add(crystal(.62,pale,point(.88,a,.12),.105))
        add(mesh_sphere(.29,rgb,(0,0,0),sub=3,metallic=.45,rough=.22,glow=.7))
        for side in (-1,1):
            add(tube([[0,-.8,0],[side*.28,-.25,.08],[0,.35,0]],.035,pale))
    elif family=="geode":
        core=trimesh.creation.icosphere(subdivisions=3,radius=.68)
        core.apply_scale([.85+scale*.12,.7+scale*.15,.8+scale*.1])
        core.visual.material=mat(deep,.92,.22,.35); add(core)
        for i in range(9+tier*2):
            a=phase+i*math.tau/(9+tier*2); r=.58+float(rng.random())*.18
            c=crystal(.48+float(rng.random())*.72,accent if i%3 else pale,point(r,a,float(rng.uniform(-.25,.25))),.10+float(rng.random())*.12)
            c.apply_transform(trimesh.geometry.align_vectors([0,0,1],np.array(point(1,a,.35))))
            add(c)
    elif family=="vortex":
        for strand in range(5):
            pts=[]
            for j in range(110):
                q=j/109; a=phase+strand*math.tau/5+q*math.tau*(2.1+tier*.12)
                r=.22+q*(1.18+.12*math.sin(q*math.pi))
                pts.append((math.cos(a)*r,(q-.5)*1.9,math.sin(a)*r))
            add(tube(pts,.027+strand*.003,accent if strand%2 else pale))
        add(mesh_sphere(.31,deep,(0,0,0),sub=3,metallic=.9,rough=.08,glow=.2))
    elif family=="wings":
        for side in (-1,1):
            for row in range(4+tier//2):
                pts=[]
                for j in range(30):
                    q=j/29
                    pts.append((side*(.12+q*(.85+row*.12)),.22+row*.11+math.sin(q*math.pi)*(.25+row*.07),-.18+row*.12+q*.18))
                add(tube(pts,.045-row*.003,accent if row%2 else pale))
                if row%2==0: add(crystal(.55+row*.1,pale,(side*(.9+row*.12),.45+row*.12,.0),.09))
        add(mesh_sphere(.28,rgb,(0,0,0),sub=3,glow=.8))
    elif family=="mist":
        for layer in range(5+tier):
            pts=[]
            for j in range(70):
                q=j/69; x=-1.35+2.7*q
                y=(layer-2)*.22+math.sin(q*math.tau+layer*.8)*(.2+layer*.015)
                z=.28*math.cos(q*math.tau*1.3+layer)
                pts.append((x,y,z))
            add(tube(pts,.035+layer*.002,accent if layer%2 else pale))
        for i in range(8):
            a=phase+i*math.tau/8
            add(mesh_sphere(.15,pale,point(.75,a,.25*math.sin(i)),scale=(1.2,.7,1),sub=2,glow=.8))
    elif family=="flame":
        add(mesh_sphere(.48,deep,(0,-.12,0),sub=3,metallic=.45,rough=.18,glow=1))
        for i in range(9+tier*2):
            a=phase+i*math.tau/(9+tier*2)
            h=.85+float(rng.random())*(.8+tier*.12)
            pts=[point(.2,a,-.4),point(.48,a+.12,.0),point(.35+float(rng.random())*.25,a-.08,h)]
            add(tube(pts,.045+float(rng.random())*.025,accent if i%2 else pale))
            add(crystal(h*.7,pale,point(.42,a,h*.32),.12))
    elif family=="frost":
        add(mesh_sphere(.38,deep,(0,0,0),sub=2,metallic=.85,rough=.08,glow=.5))
        for i in range(8):
            a=phase+i*math.tau/8
            start=point(.12,a,0); mid=point(.65,a,.05); end=point(1.25,a,.0)
            add(cyl(start,mid,.07,accent,8)); add(cyl(mid,end,.045,pale,8))
            for branch in (-1,1):
                add(cyl(mid,point(.95,a+branch*.28,.15),.035,accent,7))
            add(crystal(.42,pale,end,.09))
    elif family=="spiral":
        for strand in range(2+(seed%3)):
            pts=[]
            for j in range(150):
                q=j/149; a=phase+q*math.tau*(2.8+strand*.25)+strand*math.tau/3
                r=.18+q*(.95+strand*.08)
                pts.append((math.cos(a)*r,(q-.5)*2.1,math.sin(a)*r))
            add(tube(pts,.045 if strand==0 else .025,accent if strand%2 else pale))
        add(mesh_sphere(.22,rgb,(0,0,0),sub=3,metallic=1,rough=.05,glow=.8))
    elif family in ("sanctum","gate"):
        # Tier 3+ becomes architectural: buttresses, arches, layered vaults.
        radius=1.0 if family=="gate" else .82
        for i in range(8+(tier*2)):
            a=phase+i*math.tau/(8+tier*2)
            x,z=math.cos(a)*radius,math.sin(a)*radius
            add(cyl((x*.78,-.95,z*.78),(x, .95,z),.065,accent,10))
            add(mesh_sphere(.12,pale,(x,1.0,z),sub=2,metallic=.9,rough=.12,glow=.8))
        for ring in range(2+(tier//2)):
            add(torus(radius+ring*.18,.035 if ring==0 else .022,accent if ring%2 else pale,(.2+ring*.2,1,.1),112,10))
        for side in (-1,1):
            add(tube([[side*.28,-.7,0],[side*.55,.0,.12],[side*.38,.85,0],[side*.12,1.25,-.08]],.065,pale))
            add(crystal(.85+tier*.12,accent,(side*.42,1.15,0),.16))
        add(mesh_sphere(.32,rgb,(0,0,0),sub=3,metallic=.8,rough=.12,glow=.9))
    elif family=="crown":
        add(mesh_sphere(.38,deep,(0,-.25,0),sub=3,metallic=.85,rough=.1,glow=.55))
        for i in range(9+tier):
            a=phase+i*math.tau/(9+tier)
            r=.62+.12*math.sin(i*2.4)
            add(cyl(point(.25,a,-.2),point(r,a,.1),.055,accent,9))
            add(crystal(1.0+(i%4)*.2,pale,point(r,a,.58),.14))
        add(torus(.72,.07,accent,(.2,1,.15),100,14))
    elif family=="comet":
        add(mesh_sphere(.48,rgb,(0,0,0),scale=(1.1,.8,.9),sub=4,metallic=.75,rough=.12,glow=.85))
        for strand in range(7):
            pts=[]
            for j in range(70):
                q=j/69
                pts.append((-.2-2.0*q,.3*math.sin(q*5+strand), (strand-3)*.11+q*.22))
            add(tube(pts,.025+(strand%3)*.009,accent if strand%2 else pale))
        for i in range(7):
            a=phase+i*math.tau/7
            add(torus(.65+i*.07,.018,pale,(math.cos(a),.4,math.sin(a)),72,8))
    elif family=="blade":
        for side in (-1,1):
            add(cyl((side*.08,-1.25,0),(side*.08,1.1,0),.055,accent,8))
            add(crystal(1.6,pale,(side*.08,.45,0),.13))
        add(mesh_sphere(.28,rgb,(0,-.2,0),scale=(.8,1.5,.7),sub=3,glow=.9))
        add(torus(.48,.045,accent,(0,1,0),72,10))
    else:
        # Rare fallback identity: asymmetric relic monolith with split floating plates.
        add(mesh_sphere(.38,deep,(0,0,0),sub=3,metallic=.9,rough=.08,glow=.6))
        for i in range(7):
            a=phase+i*math.tau/7
            p=trimesh.creation.box(extents=(.3,.9,.22))
            p.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0]))
            p.apply_translation(point(.9,a,.12*math.sin(i)))
            p.visual.material=mat(accent,.85,.16,.8); add(p)

    # Higher rarity adds authored-looking structural complexity, not a shared ring cage.
    if tier>=2:
        for i in range(2+tier):
            a=phase+i*math.tau/(2+tier)
            r=1.35+.08*(i%3)
            add(mesh_sphere(.045+tier*.006,pale,point(r,a,.35*math.sin(a*2)),sub=2,metallic=.9,rough=.1,glow=1))
    if tier>=4:
        for side in (-1,1):
            for row in range(2+tier//2):
                x=side*(.35+row*.16)
                add(tube([[x,-.35,.05],[x*1.6,.25,.12],[x*2.0,.85,.0],[x*1.25,1.35,-.1]],.035+tier*.002,accent if row%2 else pale))
    if tier>=6:
        # Grand, asymmetric celestial crown and suspended shards.
        for i in range(12):
            a=phase+i*math.tau/12
            h=1.2+.35*math.sin(i*1.7)
            add(crystal(h,pale,point(1.55,a,.2*math.cos(i)),.12))
        for i in range(3):
            pts=[]
            for j in range(100):
                q=j/99; a=phase+i*math.tau/3+q*math.tau*1.6
                r=.4+1.8*q
                pts.append((math.cos(a)*r,.5*math.sin(q*math.pi*2+i),math.sin(a)*r))
            add(tube(pts,.028,accent))
    # Unique per-ID microdetail, asymmetry and palette variation.
    for i in range(4+seed%7+tier):
        a=phase+i*2.399
        p=point(.55+(i%4)*.29,a,float(rng.uniform(-.8,.8)))
        add(mesh_sphere(.025+float(rng.random())*.045,pale,p,sub=2,metallic=.9,rough=.1,glow=.9))
    return parts




def sculpted_shard(height, width, depth, rgb, seed, pos, twist=0.0):
    """A custom multi-faceted, asymmetrically cut crystal rather than a primitive cone."""
    rng=np.random.default_rng(seed)
    rings=[
        (-.52,.12),(-.34,.58),(-.08,1.0),(.18,.78),(.38,.43),(.5,.025)
    ]
    sides=7+(seed%4)
    verts=[]
    for row,(y,scale) in enumerate(rings):
        for j in range(sides):
            a=math.tau*j/sides+twist+row*.075
            wobble=1+float(rng.uniform(-.09,.09))
            verts.append([math.cos(a)*width*scale*wobble,
                          y*height,
                          math.sin(a)*depth*scale*wobble])
    faces=[]
    for row in range(len(rings)-1):
        for j in range(sides):
            a=row*sides+j; b=row*sides+(j+1)%sides
            c=(row+1)*sides+(j+1)%sides; d=(row+1)*sides+j
            if (j+row+seed)%2:
                faces.extend([(a,b,c),(a,c,d)])
            else:
                faces.extend([(a,b,d),(b,c,d)])
    faces.extend([(0,j+1 if j+1<sides else 0, (j+1)%sides) for j in range(sides)])
    mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
    mesh.apply_translation(pos)
    mesh.visual.material=mat(rgb,.88,.12,.92)
    return mesh


def atelier_parts(aura, seed):
    """Second sculptural pass: semantic signature forms, custom-cut geometry and tier finish."""
    rng=np.random.default_rng(seed ^ 0xA71E2026)
    name=str(aura.get("name",""))
    desc=str(aura.get("description",""))
    text_blob=name+" "+desc
    tier=int(aura.get("tier",0))
    rgb=css_rgb(aura.get("color","#8bdcff"))
    accent=tuple(min(1,c*.55+.38) for c in rgb)
    pale=tuple(min(1,c*.20+.76) for c in rgb)
    shadow=tuple(c*.16 for c in rgb)
    parts=[]

    # Semantic motif selection: the name takes precedence, description resolves ambiguity.
    motifs=[
        (("용","드래곤","비늘","dragon"),"wyrm"),
        (("왕관","왕","군주","왕좌"),"regalia"),
        (("꽃","장미","벚꽃","연꽃","새싹","꽃잎"),"bloom"),
        (("검","칼날","검성","창","창끝"),"edge"),
        (("달","월식","초승달","월광"),"lunar"),
        (("태양","일식","광휘","태양풍"),"solar"),
        (("심해","바다","해류","파도","고래"),"abyss"),
        (("숲","나무","고목","덩굴","잎"),"grove"),
        (("시계","시간","초침","영겁","크로노스"),"clock"),
        (("천사","천국","성역","성당","세라프"),"sanctuary"),
        (("악마","지옥","저주","마왕","심연"),"infernal"),
        (("번개","폭풍","천둥","뇌전"),"tempest"),
        (("얼음","빙하","서리","눈꽃","설원"),"glacier"),
        (("유리","거울","수정","프리즘","수정궁"),"glass"),
        (("우주","은하","성운","별","성좌","별빛"),"cosmic"),
        (("기계","엔진","기어","증기","회로"),"mechanism"),
        (("나비","날개","깃털","불사조","피닉스"),"winged"),
        (("유성","혜성","운석","별똥별"),"meteor"),
        (("유령","망령","영혼","환영","그림자"),"wraith"),
        (("문","관문","차원","포탈","차원문"),"portal"),
    ]
    motif="relic"
    for words,key in motifs:
        if any(word in text_blob for word in words):
            motif=key
            break

    phase=float(rng.uniform(0,math.tau))
    # The central sculpture is a bespoke cut form; its proportions vary independently per ID.
    core_kind=seed%6
    if core_kind==0:
        core=trimesh.creation.icosphere(subdivisions=3,radius=.48)
        v=core.vertices.copy()
        v[:,0]*=float(rng.uniform(.72,1.28))
        v[:,1]*=float(rng.uniform(.82,1.42))
        v[:,2]*=float(rng.uniform(.72,1.25))
        radial=1+.10*np.sin(v[:,0]*9+phase)*np.cos(v[:,2]*7-phase)
        core.vertices=v*radial[:,None]
    elif core_kind==1:
        vertices=np.array([
            [0,.78,0],[0,-.72,0],[.58,0,0],[-.58,0,0],[0,0,.54],[0,0,-.54]
        ],dtype=float)
        faces=np.array([
            [0,2,4],[0,4,3],[0,3,5],[0,5,2],
            [1,4,2],[1,3,4],[1,5,3],[1,2,5]
        ],dtype=int)
        core=trimesh.Trimesh(vertices=vertices,faces=faces,process=True)
        core.apply_scale([float(rng.uniform(.48,.72)),float(rng.uniform(.62,.94)),float(rng.uniform(.48,.72))])
        core=core.subdivide()
    elif core_kind==2:
        core=trimesh.creation.icosphere(subdivisions=2,radius=.52)
        v=core.vertices.copy()
        v[:,1]*=1.25
        v[:,0]*=(1+.16*np.sin(np.arctan2(v[:,2],v[:,0])*5+phase))
        core.vertices=v
    elif core_kind==3:
        core=trimesh.creation.cone(.58,1.15,sections=9+seed%7)
        core.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
        core.apply_transform(trimesh.transformations.rotation_matrix(phase,[0,1,0]))
    elif core_kind==4:
        core=trimesh.creation.icosphere(subdivisions=3,radius=.48)
        v=core.vertices.copy()
        v[:,0]+=0.12*np.sin(v[:,1]*8+phase)
        v[:,2]+=0.10*np.cos(v[:,0]*7-phase)
        core.vertices=v
    else:
        core=trimesh.creation.cylinder(radius=.43,height=1.05,sections=8+seed%9)
        core.apply_transform(trimesh.transformations.rotation_matrix(phase,[0,1,0]))
    core.visual.material=mat(shadow if tier>=5 else rgb,.86,.13,.68+tier*.035)
    parts.append(core)

    # Motif-specific hero silhouette and secondary structures.
    if motif=="wyrm":
        for side in (-1,1):
            pts=[]
            for j in range(42):
                q=j/41
                pts.append((side*(.18+1.45*q),.18+math.sin(q*math.pi*2+phase)*(.18+q*.12),.2+q*.35))
            parts.append(tube(pts,.055,accent))
            for j in range(5):
                q=.2+j*.15
                parts.append(sculpted_shard(.48+float(rng.random())*.3,.12,.16,pale,seed+j*13,(side*(.35+q*1.1),.35+q*.4,.16),twist=phase+j*.2))
        for j in range(7):
            a=phase+j*math.tau/7
            parts.append(sculpted_shard(.55,.12,.14,accent,seed+j*7,(.72*math.cos(a),-.12,.72*math.sin(a)),a))
    elif motif in ("regalia","sanctuary"):
        count=7+(seed%5)
        for j in range(count):
            a=phase+j*math.tau/count
            radius=.76+.12*math.sin(j*2.1)
            parts.append(sculpted_shard(.8+float(rng.random())*.55,.13,.17,pale,seed+j*19,(radius*math.cos(a),.48+.12*math.sin(a*3),radius*math.sin(a)),a))
            if j%2==0:
                parts.append(mesh_sphere(.085,accent,(1.05*math.cos(a),.12,1.05*math.sin(a)),sub=2,metallic=.95,rough=.1,glow=1))
        for side in (-1,1):
            parts.append(tube([[side*.25,-.6,0],[side*.72,-.1,.1],[side*.82,.62,0],[side*.4,1.12,-.08]],.055,accent))
    elif motif=="bloom":
        count=6+seed%5
        for j in range(count):
            a=phase+j*math.tau/count
            petal=mesh_sphere(.42,accent,(.62*math.cos(a),.18,.62*math.sin(a)),(.32,1.42,.22),4,.55,.2,.72)
            petal.apply_transform(trimesh.transformations.rotation_matrix(a,[0,1,0]))
            parts.append(petal)
            parts.append(sculpted_shard(.42,.10,.09,pale,seed+j*11,(.95*math.cos(a),.52,.95*math.sin(a)),a))
        parts.append(torus(.38,.045,pale,(.2,.8,.3),112,14))
    elif motif=="edge":
        for side in (-1,1):
            parts.append(sculpted_shard(2.0,.23,.12,pale,seed+int(side*3),(side*.27,.0,0),phase+side*.15))
            parts.append(tube([[side*.12,-1.0,.12],[side*.12,-.55,.2],[side*.42,-.22,.12]],.055,accent))
        parts.append(torus(.48,.055,accent,(0,1,0),96,12))
    elif motif in ("lunar","solar","cosmic","meteor"):
        for j in range(3+(seed%3)):
            pts=[]
            for k in range(100):
                q=k/99
                a=phase+j*math.tau/5+q*math.tau*(1.6+j*.12)
                r=.22+q*(1.15+.12*j)
                pts.append((math.cos(a)*r,.32*math.sin(q*math.tau*2+j),math.sin(a)*r))
            parts.append(tube(pts,.022+j*.006,accent if j%2 else pale))
        for j in range(9+seed%8):
            a=phase+j*2.399
            r=.75+float(rng.random())*.8
            parts.append(mesh_sphere(.035+float(rng.random())*.055,pale,(r*math.cos(a),float(rng.uniform(-.7,.7)),r*math.sin(a)),sub=2,metallic=.9,rough=.1,glow=1))
    elif motif in ("abyss","glacier","infernal","tempest","wraith"):
        count=7+seed%5
        for j in range(count):
            a=phase+j*math.tau/count
            height=.9+float(rng.random())*(.65+tier*.09)
            p=(.78*math.cos(a),float(rng.uniform(-.18,.22)),.78*math.sin(a))
            parts.append(sculpted_shard(height,.16,.13,accent if j%2 else pale,seed+j*17,p,a))
            if motif=="abyss":
                parts.append(tube([p,(p[0]*1.5,p[1]-.35,p[2]*1.5),(p[0]*1.85,p[1]-.75,p[2]*1.85)],.025,pale))
    elif motif=="grove":
        for side in (-1,1):
            for j in range(4):
                x=side*(.25+j*.16)
                parts.append(tube([[0,-1.05,0],[x*.55,-.35,.08],[x,.28,.12],[x*1.2,.88,.02]],.035,accent))
                leaf=mesh_sphere(.32,pale,(x,.32+j*.12,.1),(.22,1.25,.18),3,.42,.3,.45)
                leaf.apply_transform(trimesh.transformations.rotation_matrix(side*.58,[0,0,1]))
                parts.append(leaf)
    elif motif=="clock":
        for j in range(12):
            a=phase+j*math.tau/12
            parts.append(cyl((.9*math.cos(a),.9*math.sin(a),.12),(1.08*math.cos(a),1.08*math.sin(a),.12),.035,pale,8))
        parts.append(torus(.92,.065,accent,(.12,.08,1),128,16))
        parts.append(cyl((0,0,.18),(.0,.62,.18),.035,pale,10))
        parts.append(cyl((0,0,.2),(.52,-.32,.2),.027,accent,10))
    elif motif=="glass":
        for j in range(5+seed%4):
            a=phase+j*math.tau/(5+seed%4)
            parts.append(sculpted_shard(1.0+float(rng.random())*.8,.12+float(rng.random())*.08,.12,pale,seed+j*23,(.65*math.cos(a),.1,.65*math.sin(a)),a))
        parts.append(torus(.68,.025,accent,(.35,.7,.2),112,10))
    elif motif=="mechanism":
        for axis in ((1,0,0),(0,1,0),(0,0,1)):
            parts.append(torus(.72,.07,accent,axis,96,14))
        for j in range(8):
            a=phase+j*math.tau/8
            parts.append(cyl((.5*math.cos(a),-.18,.5*math.sin(a)),(.98*math.cos(a),.18,.98*math.sin(a)),.045,pale,8))
            parts.append(mesh_sphere(.09,accent,(.98*math.cos(a),.18,.98*math.sin(a)),sub=2,metallic=.95,rough=.12,glow=.8))
    elif motif=="winged":
        for side in (-1,1):
            for row in range(6):
                x=side*(.24+row*.13)
                pts=[(side*.16,-.15,.0),(x,.12+row*.1,.05),(side*(.9+row*.16),.72+row*.08,-.08),(side*(.62+row*.18),1.0+row*.08,-.16)]
                parts.append(tube(pts,.045-row*.003,pale if row%2 else accent))
                if row%2==0:
                    parts.append(sculpted_shard(.72,.11,.08,accent,seed+row*5,(side*(.75+row*.15),.5+row*.12,-.08),side*.2))
    elif motif=="portal":
        for ring in range(3):
            parts.append(torus(.72+ring*.23,.035+ring*.008,accent if ring%2 else pale,(.12+ring*.24,.1,.9),128,12))
        for side in (-1,1):
            parts.append(tube([[side*.58,-1.05,0],[side*.9,-.45,.1],[side*.82,.45,.05],[side*.48,1.12,0]],.07,accent))

    # Bespoke cut ornaments: count, twist, placement and profile are ID-specific.
    shard_count=4+(seed%5)+tier
    for j in range(shard_count):
        a=phase+j*math.tau/shard_count+float(rng.uniform(-.12,.12))
        r=.92+float(rng.uniform(-.18,.36))
        h=.38+float(rng.random())*(.65+tier*.14)
        p=(r*math.cos(a),float(rng.uniform(-.48,.42)),r*math.sin(a))
        parts.append(sculpted_shard(h,.07+float(rng.random())*.09,.08+float(rng.random())*.07,
                                    accent if j%3 else pale,seed+j*29,p,a))
    # Individually designed orbital armature, deliberately non-coplanar and unbalanced.
    ring_count=1+(seed%3)+(tier//3)
    for j in range(ring_count):
        axis=rng.normal(size=3)
        radius=.92+float(rng.random())*.58
        parts.append(torus(radius,.012+float(rng.random())*.024,
                           pale if j%2 else accent,axis,96+(seed+j*7)%48,8+(j%4)*2))
    # Rarity finish: more complex architecture, not merely a larger glow value.
    if tier>=4:
        for side in (-1,1):
            for row in range(2+tier//2):
                x=side*(.38+row*.18)
                parts.append(tube([[side*.18,-.28,.12],[x,.22,.16],[side*(1.1+row*.12),.78,.02],[side*(.72+row*.2),1.35,-.1]],.035+tier*.003,accent if row%2 else pale))
    if tier>=6:
        for j in range(8+tier):
            a=phase+j*math.tau/(8+tier)
            parts.append(sculpted_shard(1.05+float(rng.random())*.65,.12,.13,pale,seed+j*31,(1.45*math.cos(a),.28,1.45*math.sin(a)),a))
        parts.append(torus(1.82,.045,pale,(.42,.18,.76),160,16))
    if tier>=7:
        # Apex rarity receives a distinctive crown-vault with suspended keystones.
        for j in range(5):
            a=phase+j*math.tau/5
            p=(1.9*math.cos(a),1.05+.15*math.sin(a*2),1.9*math.sin(a))
            parts.append(mesh_sphere(.11,pale,p,sub=3,metallic=1,rough=.08,glow=1))
            parts.append(tube([[.25*math.cos(a),.35,.1],[.95*math.cos(a),.72,.05],p],.035,accent))
    return parts


catalog_path=Path("supabase/aura_catalog.json")
if not catalog_path.exists():
    raise SystemExit("supabase/aura_catalog.json is required to build unique aura assets")
catalog=json.loads(catalog_path.read_text(encoding="utf-8"))
if len(catalog)!=1000 or len({a["id"] for a in catalog})!=1000:
    raise SystemExit("Aura catalog must contain exactly 1,000 unique IDs")

print(f"Building all {len(catalog)} name- and rarity-specific aura GLB models")

for index,aura in enumerate(catalog):
    aura_id=aura["id"]
    seed=int.from_bytes(aura_id.encode("utf-8"),"little") % (2**32-1)
    rgb=css_rgb(aura.get("color","#8bdcff"))
    scene=trimesh.Scene()
    parts=themed_parts(aura,seed) + atelier_parts(aura,seed)
    for i,m in enumerate(parts):
        if hasattr(m,"visual"):
            shade=0.78+((seed+i*37)%27)/100
            base=rgb if i%4 in (0,1) else (tuple(min(1,c*.58+.36) for c in rgb) if i%4==2 else tuple(min(1,c*.24+.72) for c in rgb))
            part_rgb=tuple(min(1.0,c*shade) for c in base)
            m.visual.material=mat(part_rgb,.58+((seed+i*13)%39)/100,.075+((seed+i*3)%42)/100,.58+((seed+i*7)%48)/100)
        scene.add_geometry(m,geom_name=f"{aura_id}_mesh_{i:03d}",node_name=f"{aura_id}_part_{i:03d}")
    bounds=scene.bounds
    center=(bounds[0]+bounds[1])/2
    extent=max(bounds[1]-bounds[0])
    scale=2.65/(extent or 1)
    transform=np.eye(4); transform[:3,:3]*=scale; transform[:3,3]=-center*scale
    scene.apply_transform(transform)
    out=OUT/f"{aura_id}.glb"
    scene.export(out)
    if index%25==0 or index==len(catalog)-1:
        print(f"generated {index+1}/{len(catalog)}: {aura_id} ({out.stat().st_size} bytes)")
