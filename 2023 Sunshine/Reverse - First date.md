# Chall Description
I'm Excited, this is my first date in years but this time it's a Play Date!

Sadly I'm locked out of it so if you could help me get in that would be great!

Files: first_date.pdx.zip

# Write up

Unzipping the file we obtain a pdx file. Quick google shows that this is a lua compiled file, and from the names we can assume that it's related to the Playdate simulator. 

From here I used https://github.com/cranksters/playdate-reverse-engineering.
This extracted a luac file, which could then be run through unluac (https://github.com/scratchminer/unluac) to obtain the source code used:

```
import("./CoreLibs/graphics")
print("Figure out my code and I'll give you a flag!")
print("Turn the crank to reset the pin. ")
local gfx = playdate.graphics
playdate.display.setRefreshRate(50)
gfx.setBackgroundColor(gfx.kColorWhite)
function generateFlag()
	local flag = ""
	for i = 1, 64 do
		flag = flag .. string.char(math.random(32, 126))
	end
	return flag
end
function makeTextDisplayable(text)
	local displayableText = ""
	for i = 1, #text do
		local char = text:sub(i, i)
		if "_" == char then
			displayableText = displayableText .. "__"
		elseif "*" == char then
			displayableText = displayableText .. "**"
		else
			displayableText = displayableText .. char
		end
	end
	return displayableText
end
noiseSeed = 1234567
math.randomseed(noiseSeed)
pressedButtons = ""
counter = 0
buttons = {
	"left",
	"right",
	"up",
	"down",
	"A",
	"B"
}
function generateOrder()
	local pinSeed = ""
	for i = 1, 20 do
		pinSeed = pinSeed .. i
	end
	return pinSeed
end
function playdate.cranked(change, acceleratedChange)
	print("Cranked! " .. change .. " " .. acceleratedChange)
	pressedButtons = ""
	counter = 0
end
function clean(input)
	local cleaned = ""
	for i = 1, #input, 2 do
		local pair = input:sub(i, i + 1)
		local num = tonumber(pair)
		num = num % 26 + 65
		cleaned = cleaned .. string.char(num)
	end
	return cleaned
end
index = ""
lastPressed = "Press a button!"
function playdate.update()
	gfx.clear(gfx.kColorWhite)
	counter = counter + 1
	gfx.drawTextAligned(generateFlag(), 200.0, 120.0, kTextAlignment.center)
	for i = 1, #buttons do
		if playdate.buttonJustPressed(buttons[i]) then
			pressedButtons = pressedButtons .. i
			lastPressed = buttons[i]
		end
	end
	gfx.drawTextAligned(lastPressed, 200.0, 160.0, kTextAlignment.center)
	gfx.drawTextAligned(makeTextDisplayable(pressedButtons), 200.0, 180.0, kTextAlignment.center)
	gfx.drawTextAligned("Rotate the crank to reset the challenge.", 200.0, 200.0, kTextAlignment.center)
	if pressedButtons == generateOrder() then
		print("Pin entered correctly!")
		gfx.setFont(gfx.font.kVariantBold)
		cleaned = clean(pressedButtons)
		print("Flag: sun{" .. cleaned .. "}")
		gfx.drawTextAligned([[
Flag: 
sun{]] .. cleaned .. "}", 200.0, 80.0, kTextAlignment.center)
	end
end
```
At this stage, I installed the SDK to run the game in the simulator. Opened the console, and figured I can call any function I want from the console. So the pin is just generateOrder(). The game is running on a loop and always checking if pressedButtons is the same as the generateOrder(), so we can just change it in memory directly from the console with `pressedButtons = generateOrder()` and the flag is displayed both in the console and in the simulated game.