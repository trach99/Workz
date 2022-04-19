// v0.9
// javascript

function gsmInstructions(opCode) {
	
	switch (opCode) {
		case "A4": return "SELECT";
		case "F2": return "STATUS";
		case "B0": return "READ BINARY";
		case "D6": return "UPDATE BINARY";
		case "B2": return "READ RECORD";
		case "DC": return "UPDATE RECORD";
		case "A2": return "SEEK";
		case "32": return "INCREASE";
		case "20": return "VERIFY CHV";
		case "24": return "CHANGE CHV";
		case "26": return "DISABLE CHV";
		case "28": return "ENABLE CHV";
		case "2C": return "UNBLOCK CHV";
		case "04": return "INVALIDATE";
		case "44": return "REHABILITATE";
		case "88": return "RUN GSM ALGORITHM";
		case "FA": return "SLEEP";
		case "C0": return "GET RESPONSE";
		case "10": return "TERMINAL PROFILE";
		case "C2": return "ENVELOPE";
		case "12": return "FETCH";
		case "14": return "TERMINAL RESPONSE";
	}
}



function onCommand(s) {
	
    line1 = "// [" + gsmInstructions(s.substring(2, 4)) + "]";
	
	line2 = "I: ";
	i = 0;
	while (s.charAt(i) != '|') {
		line2 = line2 + s.charAt(i++);
		if (i % 2 == 0)
			line2 = line2 + ' ';
	}
	
	i++; // skip the "|"
	
	line3 = "O: ";
	while (i < s.length) {
		line3 = line3 + s.charAt(i++);
		if (i % 2 == 1)
			line3 = line3 + ' ';
	}
	
	return line1 + '\r\n' + line2 + '\r\n' + line3 + '\r\n';
}



function onReset(s) {}
