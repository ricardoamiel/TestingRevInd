"use client";
import Link from "next/link";
import React from "react";

function page() {
  return (
    <div className="flex flex-col justify-center items-center h-[100vh]">
      <h1 className="font-bold text-3xl">Proyecto Base de Datos</h1>
      <div className="flex">
        <div>Integrantes:</div>
        <div className="ml-2">
          <ul>
            <li>Gonzalo Perea</li>
            <li>Isabella Romero</li>
            <li>Josué Velo</li>
            <li>Ricardo Acuña</li>
            <li>Rodrigo Lauz</li>
          </ul>
        </div>
      </div>
      <div className="flex mt-6">
        <Link className="bg-blue-500 text-white p-2 rounded-md m-2 hover:bg-blue-700" href="/p2">
          Ir a P2
        </Link>
        <Link className="bg-red-500 text-white p-2 rounded-md m-2 hover:bg-red-700" href="/p3">
          Ir a P3
        </Link>
      </div>
    </div>
  );
}

export default page;
