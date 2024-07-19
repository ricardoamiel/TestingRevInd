"use client";
import React from "react";

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
    | undefined | any;
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
    | undefined | any;
  hasData: boolean;
}
function ResponseTable({
  searchResults,
  searchPostgresSQLResults,
  hasData,
}: responseTableProps) {
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
              {searchPostgresSQLResults?.results.map((result: any, index: number) => (
                <tr
                  key={index}
                  className=" even:bg-slate-400 odd:bg-slate-800 even:bg-opacity-10 odd-bg-opacity:10"
                >
                  <td>{result.track_name}</td>
                  <td>{result.track_artist}</td>
                  <td>{result.track_album_name}</td>
                  <td className="line-clamp-4 max-w-[45vw]">{result.lyrics}</td>
                  <td>{result.score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ResponseTable;
