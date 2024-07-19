"use client";
import React, { useState } from "react";
import Image from "next/image";
import DownloadButton from "@/app/assets/downloadIcon.png";

const fetchURL = "http://localhost:5000";

export interface searchQueryResponse {
  searchResults?:
    | {
        results: [
          {
            doc_id: number;
            score: number;
          }
        ];
        time: number;
      }
    | undefined;
}

export interface searchPostgresSQLResponse {
  searchPostgresSQLResults:
    | {
        results: [
          {
            lyrics: string;
            score: number;
            track_album_name: string;
            track_artist: string;
            track_name: string;
          }
        ];
        time: number;
      }
    | undefined;
}

export interface responseTableProps {
  searchResults?:
    | {
        results: [
          {
            doc_id: number;
            score: number;
          }
        ];
        time: number;
      }
    | undefined
    | any;
  searchPostgresSQLResults?:
    | {
        results: [
          {
            lyrics: string;
            score: number;
            track_album_name: string;
            track_artist: string;
            track_name: string;
          }
        ];
        time: number;
      }
    | undefined
    | any;
  hasData: boolean;
}
function ResponseTableP2({
  searchResults,
  searchPostgresSQLResults,
  hasData,
}: responseTableProps) {
  const [songData, setSongData] = useState<any>(undefined);
  const [viewableData, setViewableData] = useState(false);

  async function getSongDataFromDocID(doc_id: number) {
    const response = await fetch(`${fetchURL}/document?doc_id=${doc_id}`);
    const data = await response.json();
    console.log(data);
    setSongData(data);
    setViewableData(true);
  }

  if (!hasData) {
    return <></>;
  }
  return (
    <div className="mt-6">
      <div className="flex justify-evenly">
        <div className="bg-white bg-opacity-10 p-10 rounded-md my-3 w-[35vw]">
          <h2 className="text-2xl">Resultados de búsqueda (In-Memory)</h2>
          <div className="overflow-hidden rounded-lg mt-4">
            <table className="w-full text-center">
              <thead>
                <tr className="bg-slate-400 bg-opacity-10">
                  <th>Doc ID</th>
                  <th>Score</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {searchResults?.results.map((result: any, index: number) => (
                  <tr
                    key={index}
                    className=" even:bg-slate-400 odd:bg-slate-800 even:bg-opacity-10 odd-bg-opacity:10"
                  >
                    <td>{result.doc_id}</td>
                    <td>{result.score.toFixed(4)}</td>
                    <td>
                      <button
                        onClick={() => getSongDataFromDocID(result.doc_id)}
                        className="text-white hover:text-gray-500"
                      >
                        <Image
                          src={DownloadButton}
                          alt="Download"
                          width={20}
                          height={20}
                        />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="flex flex-col justify-evenly align-middle">
          <div className="bg-white bg-opacity-10 p-10 rounded-md my-3">
            Tiempo de búsqueda (In-Memory): {searchResults?.time.toFixed(4)}
            ms
          </div>
          <div className="bg-white bg-opacity-10 p-10 rounded-md">
            Tiempo de búsqueda (PostgresSQL):{" "}
            {searchPostgresSQLResults?.time.toFixed(4)}
            ms
          </div>
        </div>
      </div>

      {viewableData && (
        <div className="bg-white bg-opacity-10 p-10 rounded-md my-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl">Información de la canción</h2>
            <button
              className="bg-red-700 hover:bg-red-900 p-2 rounded-md"
              onClick={() => {
                setSongData(undefined);
                setViewableData(false);
              }}
            >
              Cerrar
            </button>
          </div>
          <div className="overflow-hidden rounded-lg mt-4">
            <table className="w-full text-center">
              <thead>
                <tr className="bg-slate-400 bg-opacity-10">
                  <th>Nombre de la canción</th>
                  <th>Artista</th>
                  <th>Letra</th>
                </tr>
              </thead>
              <tbody>
                <tr className=" even:bg-slate-400 odd:bg-slate-800 even:bg-opacity-10 odd-bg-opacity:10">
                  <td>{songData.track_name}</td>
                  <td>{songData.track_artist}</td>
                  <td className="max-w-[45vw] text-left">
                    {songData.lyrics}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-white bg-opacity-10 p-10 rounded-md">
        <h2 className="text-2xl">Resultados de búsqueda (PostgresSQL)</h2>
        <div className="overflow-hidden rounded-lg mt-4">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-400 bg-opacity-10">
                <th>Nombre de la canción</th>
                <th>Artista</th>
                <th>Álbum</th>
                <th>Letra</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {searchPostgresSQLResults?.results.map(
                (result: any, index: number) => (
                  <tr
                    key={index}
                    className=" even:bg-slate-400 odd:bg-slate-800 even:bg-opacity-10 odd-bg-opacity:10"
                  >
                    <td>{result.track_name}</td>
                    <td>{result.track_artist}</td>
                    <td>{result.track_album_name}</td>
                    <td className="line-clamp-4 max-w-[45vw]">
                      {result.lyrics}
                    </td>
                    <td>{result.score.toFixed(4)}</td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ResponseTableP2;
