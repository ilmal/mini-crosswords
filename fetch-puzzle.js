const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

async function fetchPuzzle() {
  try {
    const response = await axios.get('https://www.nytimes.com/svc/crosswords/v6/puzzle/mini.json', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Games-Auth-Bypass': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nytimes.com/crosswords/game/mini',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers'
      },
      decompress: true
    });

    const puzzleData = response.data;
    console.log('API Response:', JSON.stringify(puzzleData, null, 2)); // Log response for debugging

    // Validate response structure
    if (!puzzleData || !puzzleData.body || !Array.isArray(puzzleData.body) || !puzzleData.body[0]) {
      throw new Error('Invalid API response: missing body or body[0]');
    }

    let publicationDate = puzzleData.body[0].publicationDate;
    if (!publicationDate || !/^\d{4}-\d{2}-\d{2}$/.test(publicationDate)) {
      console.warn(`Invalid or missing publicationDate: ${publicationDate}. Using current date as fallback.`);
      const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      publicationDate = today;
    }

    const fileName = `${publicationDate}.json`;
    const filePath = path.join('puzzles', fileName);

    // Check for duplicates
    try {
      await fs.access(filePath);
      console.log(`Puzzle for ${publicationDate} already exists, skipping.`);
      return;
    } catch (error) {
      // File doesn't exist, proceed to save
    }

    // Ensure puzzles directory exists
    await fs.mkdir('puzzles', { recursive: true });

    // Save puzzle JSON
    await fs.writeFile(filePath, JSON.stringify(puzzleData, null, 2));

    // Update puzzle-list.json
    let puzzleList = [];
    try {
      const listContent = await fs.readFile('puzzles/puzzle-list.json', 'utf8');
      puzzleList = JSON.parse(listContent);
    } catch (error) {
      // File doesn't exist yet, initialize empty list
    }

    // Add new puzzle to list if not already present
    if (!puzzleList.some(puzzle => puzzle.date === publicationDate)) {
      puzzleList.push({ date: publicationDate, file: fileName });
      await fs.writeFile('puzzles/puzzle-list.json', JSON.stringify(puzzleList, null, 2));
    }

    console.log(`Saved puzzle for ${publicationDate}`);
  } catch (error) {
    console.error('Error fetching puzzle:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', JSON.stringify(error.response.data, null, 2));
    }
    process.exit(1);
  }
}

fetchPuzzle();
