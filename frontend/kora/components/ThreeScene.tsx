"use client";

import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import ThreeGlobe from "three-globe";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

const GlobeWithCountries: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [countries, setCountries] = useState<any[]>([]);

  useEffect(() => {
    // Fetch GeoJSON for countries
    fetch(
      "https://vasturiano.github.io/three-globe/example/country-polygons/ne_110m_admin_0_countries.geojson"
    )
      .then((res) => res.json())
      .then((geoJson) => setCountries(geoJson.features));
  }, []);

  // const ThreeScene: React.FC = () => {
  // const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (typeof window !== 'undefined') {
      //  Initialize Three.js scene here
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x000000);
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      containerRef.current?.appendChild(renderer.domElement);
      camera.position.z = 5;

      // const geometry = new THREE.BoxGeometry();
      const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

      
      const globe = new ThreeGlobe()
        .globeImageUrl("//unpkg.com/three-globe/example/img/earth-night.jpg")
        .polygonsData(countries)
        .polygonCapColor(() => "rgba(252, 250, 250, 0.95)")  // fill color
        .polygonSideColor(() => "rgba(54, 203, 54, 0.75)")  // sides
        .polygonStrokeColor(() => "#f0d584ff");            // border

      scene.add(globe);

      // const cube = new THREE.Mesh(geometry, material);
      // scene.add(cube);

      // // Render the scene and camera
      // renderer.render(scene, camera);


      const renderScene = () => {
        // globe.rotation.x += 0.01;
        globe.rotation.y += 0.01;
        renderer.render(scene, camera);
        requestAnimationFrame(renderScene);
      };

      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 2;
      controls.maxDistance = 10;

      // // Call the renderScene function to start the animation loop
      // renderScene();

      const handleResize = () => {
        const width = window.innerWidth;
        const height = window.innerHeight;

        camera.aspect = width / height;
        camera.updateProjectionMatrix();

        renderer.setSize(width, height);
      };

      window.addEventListener('resize', handleResize);
      // Call the renderScene function to start the animation loop
      renderScene();

      // Clean up the event listener when the component is unmounted
      
      return () => {
        window.removeEventListener("resize", handleResize);
        containerRef.current?.removeChild(renderer.domElement);
        renderer.dispose();
      };
    }
  }, [countries]);
  return <div ref={containerRef} />;
};
export default GlobeWithCountries;
