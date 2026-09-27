'use client';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles } from '@react-three/drei';
import { useRef } from 'react';
import type { Mesh } from 'three';
function Beacon(){const ref=useRef<Mesh>(null);useFrame((_,delta)=>{if(ref.current)ref.current.rotation.y+=delta*.35});return <Float speed={2}><mesh ref={ref}><octahedronGeometry args={[1,0]}/><meshStandardMaterial color="#ff641e" emissive="#ff3d00" emissiveIntensity={2}/></mesh></Float>}
export function WorldScene(){return <Canvas camera={{position:[0,0,5],fov:45}} dpr={[1,1.5]}><color attach="background" args={['#10131a']}/><ambientLight intensity={1}/><pointLight position={[3,3,3]} color="#ff641e" intensity={35}/><Beacon/><Sparkles count={70} scale={8} size={2} speed={.35}/></Canvas>}
