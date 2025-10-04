import Image from "next/image";
import ThreeScene from "../../../components/ThreeScene";
import Globe from 'react-globe.gl';

export default function Home() {
  return (
    <main style={{ width: "100vw", height: "100vh", margin: 0, padding: 0 }}>
      <ThreeScene />
    </main>
  );
}
