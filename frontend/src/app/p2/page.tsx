"use client";
import React, { useState } from "react";
import ResponseTableP2, {
  searchPostgresSQLResponse,
  searchQueryResponse,
} from "./_components/responseTable";

export default function Home() {
  const fetchURL = "http://localhost:5000";
  const [usableData, setUsableData] = useState(false);
  const [searchResults, setSearchResults] = useState<
    searchQueryResponse | undefined
  >(undefined);
  const [searchPostgresSQLResults, setSearchPostgresSQLResults] = useState<
    searchPostgresSQLResponse | undefined
  >(undefined);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSearch() {
    const queryText = (
      document.getElementById("queryTextField") as HTMLInputElement
    ).value;
    const kValue = (document.getElementById("kValueField") as HTMLInputElement)
      .value;
    const languageSelect = (
      document.getElementById("languageSelectField") as HTMLSelectElement
    ).value;

    if (!queryText || !kValue || !languageSelect) {
      alert("Please fill in all fields");
      return;
    }

    setIsLoading(true);

    const response = await fetch(
      `${fetchURL}/search?query=${queryText}&k=${kValue}&language=${languageSelect}`
    );
    const data = await response.json();
    setSearchResults(data);

    const response_pg = await fetch(
      `${fetchURL}/search_postgresql?query=${queryText}&k=${kValue}&language=${languageSelect}`
    );
    const data_pg = await response_pg.json();
    setSearchPostgresSQLResults(data_pg);

    setUsableData(true);
    setIsLoading(false);
  }
  async function handleViewInvertedIndex() {
    console.log("Viewing Inverted Index");
  }
  async function handleViewPostgresSQL() {
    console.log("Viewing PostgresSQL");
  }
  return (
    <>
      <div className="flex flex-col justify-center items-center">
        <h1 className="text-3xl font-bold">
          Spotify Filter-Song-by-Text Search
        </h1>
        <p>Search for songs on Spotify by text</p>
      </div>

      <div className="text-black my-3">
        <div className="flex">
          <input
            type="text"
            id="queryTextField"
            placeholder="Search for songs"
            className="w-full p-2 my-4 rounded-md grow mr-3"
          />
          <input
            type="number"
            id="kValueField"
            placeholder="k"
            className="p-2 my-4 rounded-md grow-0 w-[10%]"
          />
        </div>
        <div className="flex justify-between">
          <select id="languageSelectField" className="rounded-md p-2">
            <option value="en">English</option>
            <option value="es">Spanish</option>
          </select>
          <div>
            <button
              onClick={handleViewInvertedIndex}
              className={`p-2 rounded-md text-white hover:text-gray-300 ${
                usableData ? "" : "hidden"
              }`}
            >
              Ver GET Inverted Index
            </button>
            <button
              onClick={handleViewPostgresSQL}
              className={`p-2 rounded-md text-white hover:text-gray-300 ${
                usableData ? "" : "hidden"
              }`}
            >
              Ver GET PostgresSQL
            </button>
            <button
              onClick={handleSearch}
              className="bg-blue-600 p-2 rounded-md text-white hover:bg-blue-800"
            >
              Search
            </button>
          </div>
        </div>
      </div>
      {isLoading ? (
        // Loading spinner using a rounded div with a border
        <div className="flex justify-center items-center h-96">
          <div className="rounded-full border-4 border-r-0 border-b-0 border-gray-200 h-20 w-20 animate-spin"></div>
        </div>
      ) : (
        <ResponseTableP2
          searchResults={searchResults}
          searchPostgresSQLResults={searchPostgresSQLResults}
          hasData={usableData}
        />
      )}
    </>
  );
}
