fs=require('fs');
fs.writeFileSync('channels.json', JSON.stringify({channels:fs.readFileSync('channels.txt').toString().split('\n').map(name=>{return{
	name,
	issue: "main",
	alias: name ,
	groups:{
        	main: "purple"
      	}
}}),
"emojis": {
    "red": "🇷 🇺 ",
    "blue": "🌎",
    "purple": "⚖️",
    "tech": "💻",
    "economy":"💰",
    "other": "📰",
    "moscow": "🌆",
    "entertainment": "🎭"
  },
  "colors": {
    "red": "🟥",
    "blue": "🟦",
    "purple": "🟪",
    "tech": "⬛",
    "economy": "🟨",
    "other": "⬜",
    "moscow": "⬜",
    "entertainment": "🟩"
  },
  "default_groups": {
    "main": "purple",
  }
}, null, '\t'))
