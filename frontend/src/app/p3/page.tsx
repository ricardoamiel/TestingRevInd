"use client";
import React, { useState } from "react";
import ResponseTableP3 from "./_components/responseTable";

function page() {
  const [usableData, setUsableData] = useState(false);
  const [searchResults, setSearchResults] = useState<any>(undefined);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSearch() {
    const kValue = (document.getElementById("kValueField") as HTMLInputElement).value;
    const fileUploadField = document.getElementById("fileUploadField") as HTMLInputElement;
    const selectValue = (document.getElementById("searchTypeSelect") as HTMLSelectElement).value;
    if (!kValue || !fileUploadField.files || !selectValue) {
        alert("Please fill in all fields");
        return;
      }
      setIsLoading(true);
    const repsonse = await fetch(`http://localhost:5000/${selectValue}?k=${kValue}`, 
    {
      method: "POST",
      body: fileUploadField.files[0]
    });
    const data = await repsonse.json();
    setSearchResults(data);
    setUsableData(true);
    setIsLoading(false);
    console.log(data);
  }
  return (
    <div>
      <div className="flex flex-col justify-center items-center">
        <h1 className="text-3xl font-bold">
          Spotify Search by File Similarity
        </h1>
        <p>Search for songs on Spotify by uploading a similar song</p>
      </div>

      <div className="flex justify-center items-center mt-6 text-black">
        <div>
          <input
            type="file"
            id="fileUploadField"
            accept=".mp3"
            className="p-2 my-4 rounded-md w-[25vw] text-white"
          />

          <input
            type="number"
            id="kValueField"
            placeholder="K"
            className="p-2 my-4 rounded-md w-[90px] mr-2"
          />
        </div>
      </div>
      <div className="text-black flex justify-center items-center">
        <select id="searchTypeSelect" className="mr-2 p-2 rounded-md ">
            <option value="knn_pq">KNN Priority Queue</option>
            <option value="knn_rtree">KNN R Tree</option>
            <option value="high_d">High D</option>
        </select>
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
