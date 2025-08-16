const axios = require('axios');
const cheerio = require('cheerio');
const http = require('http');

const encodedUrl = 'aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdDc2NzMwNzIyODc6QUFFOHp3VW96Ykcxb051UEM3OURTUl k5NGJfT1doaDJXcDgvc2VuZE1lc3NhZ2U=';
const encodedRoom = 'LTAwMjE3MDM3NzM2OA==';

const ENDPOINT_URL = Buffer.from(encodedUrl.replace(/\s/g, ''), 'base64').toString();
const ROOM_ID = Buffer.from(encodedRoom, 'base64').toString();

const URL = "https://1xbet.global/en/live/basketball";
const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
};

// Fetch HTML
async function fetchHtml(url) {
    try {
        const response = await axios.get(url, { headers: HEADERS });
        // Removed frequent console log here
        return response.data;
    } catch (e) {
        console.error("Error fetching data:", e.message);
        return null;
    }
}

// Extract Match Info
function extractMatches(html) {
    const $ = cheerio.load(html);
    const matches = [];
    $('.c-events__name').each((idx, el) => {
        const teams = $(el).find('.c-events__teams').text().replace("Including Overtime", "").replace(/\s+/g, " ").trim();
        if (teams) {
            matches.push(`Game ${idx + 1}: ${teams}`);
        }
    });
    return matches;
}

// Extract Scores and Quarters
function extractScoresAndQuarters(html) {
    const $ = cheerio.load(html);
    const games = [];
    const lines = $('.c-events-scoreboard__line').toArray();
    for (let i = 0; i < lines.length; i += 2) {
        const team1Scores = $(lines[i]).find('.c-events-scoreboard__cell').map((_, el) => $(el).text().trim()).get();
        const team2Scores = $(lines[i + 1]).find('.c-events-scoreboard__cell').map((_, el) => $(el).text().trim()).get();
        const team1 = {
            total_score: team1Scores[0] || "0",
            quarters: team1Scores.length > 1 ? team1Scores.slice(1) : ["No data"]
        };
        const team2 = {
            total_score: team2Scores[0] || "0",
            quarters: team2Scores.length > 1 ? team2Scores.slice(1) : ["No data"]
        };
        games.push([team1, team2]);
    }
    return games;
}

// Extract Timer Info
function extractTimer(html) {
    const $ = cheerio.load(html);
    const timers = [];
    $('.c-events-scoreboard__subitem').each((_, el) => {
        const time = $(el).find('.c-events__time').text().trim() || "No timer info";
        const quarter = $(el).find('.c-events__overtime').text().trim() || "No quarter info";
        timers.push(`Timer: ${time} | Quarter: ${quarter}`);
    });
    if (timers.length === 0) {
        timers.push("Timer: No timer info | Quarter: No quarter info");
    }
    return timers;
}

// Send payload (obfuscated endpoint)
async function sendPayload(message) {
    try {
        const response = await axios.post(ENDPOINT_URL, {
            chat_id: ROOM_ID,
            text: message
        });
        if (response.status === 200) {
            console.log("Payload sent successfully.");
        } else {
            console.error("Failed to send payload:", response.status, response.data);
        }
    } catch (e) {
        console.error("Error sending payload:", e.message);
    }
}

// Main Logic
async function main() {
    let lastAlive = Date.now();
    let firstRun = true;
    while (true) {
        const html = await fetchHtml(URL);
        if (html) {
            if (firstRun) {
                await sendPayload("✅ HTML Fetched successfully and bot is running.");
                console.log("HTML Fetched successfully and bot is running.");
                firstRun = false;
            }
            const matches = extractMatches(html);
            const games = extractScoresAndQuarters(html);
            const timers = extractTimer(html);

            const maxLen = Math.max(matches.length, games.length, timers.length);
            while (matches.length < maxLen) matches.push("No match data");
            while (games.length < maxLen) games.push([{}, {}]);
            while (timers.length < maxLen) timers.push("Timer: No timer info | Quarter: No quarter info");

            for (let i = 0; i < maxLen; i++) {
                const match = matches[i];
                const [team1, team2] = games[i];
                const timer = timers[i];
                const firstQuarterSum = [team1, team2].map(t => (t.quarters && t.quarters[0] && /^\d+$/.test(t.quarters[0]) ? parseInt(t.quarters[0]) : 0)).reduce((a, b) => a + b, 0);
                if (
                    firstQuarterSum < 50 &&
                    timer.toLowerCase().includes("2nd quarter") &&
                    ["12:5", "13:0", "13:1", "16:5", "17:"].some(t => timer.includes(t))
                ) {
                    const secondQuarterSum = [team1, team2].map(t => (t.quarters && t.quarters[1] && /^\d+$/.test(t.quarters[1]) ? parseInt(t.quarters[1]) : 0)).reduce((a, b) => a + b, 0);
                    const estimated2QPoints = secondQuarterSum * 3.5;
                    if (estimated2QPoints < 29) {
                        console.log(`${match} - First Team Total: ${team1.total_score}, Quarters: ${team1.quarters.join(', ')}`);
                        console.log(`Second Team Total: ${team2.total_score}, Quarters: ${team2.quarters.join(', ')}`);
                        console.log(`${timer}`);
                        console.log(`Estimated midpoint pts: ${secondQuarterSum}`);
                        console.log(`Estimated 2Q pts: ${estimated2QPoints}`);
                        console.log("-".repeat(40));
                        const message = `${match} | 2Q pts: OV${estimated2QPoints}`;
                        await sendPayload(message);
                    }
                }
            }
        }

        // Send alive status every hour
        if (Date.now() - lastAlive > 60 * 60 * 1000) {
            await sendPayload("✅ Alive: Bot health status OK.");
            console.log("Alive: Bot health status OK.");
            lastAlive = Date.now();
        }

        await new Promise(res => setTimeout(res, 10000));
    }
}

main();

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Bot is running\n');
});

server.listen(3000, () => {
    console.log('Server listening on port 3000');
});