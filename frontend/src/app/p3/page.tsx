"use client";
import React, { useState } from "react";
import ResponseTableP3 from "./_components/responseTable";

function page() {
  const [usableData, setUsableData] = useState(false);
  const [searchResults, setSearchResults] = useState<any>(undefined);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSearch() {
    console.log("Searching");
  }
  return (
    <div>
      <div className="flex flex-col justify-center items-center">
        <h1 className="text-3xl font-bold">
          Spotify Search by File Similarity
        </h1>
        <p>Search for songs on Spotify by uploading a similar song</p>
      </div>

      <div className="flex justify-center items-center mt-6">
        <div>
          <input
            type="file"
            id="fileUploadField"
            accept=".mp3"
            className="p-2 my-4 rounded-md w-[25vw]"
          />
          
          <input
            type="number"
            id="kValueField"
            placeholder="K"
            className="p-2 my-4 rounded-md w-[90px] mr-2"
          />
        </div>

        <button
          onClick={handleSearch}
          className="bg-blue-600 p-2 rounded-md text-white hover:bg-blue-800"
        >
          Search
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center mt-6">
          <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <ResponseTableP3 responseData={searchResults} usableData={usableData} />
      )}
    </div>
  );
}

export default page;
