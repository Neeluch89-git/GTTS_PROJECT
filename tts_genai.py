from google import genai 

from google.genai import types 

import wave 

from pydub import AudioSegment 

import os 

import time 

 

# === USER CONFIGURATION === 

API_KEY = "AIzaSyDGZcGBVCO1gg6bXmYFrrG4pZjpBESHwnY" 
VOICE_NAME = "Puck"   # Example voice 

TEMPERATURE = 0.7        # Control expressiveness 

SPEAKING_RATE = 0.9 

PITCH = -2.0 

VOLUME_GAIN_DB = 2.0 

 

STORY_TEXT = """ Say in commedy way tone: ఒక ఊరి లో ప్రతి సంవత్సరం దేవుడిని ఊరేగింపు తీసుకెళ్లే సాంప్రదాయం ఉండేది. ప్రతి సంవత్సరం ఊళ్ళో వారంతా పండగ చేసుకుని, పూజలు చేసి, ఊరేగింపు కోసం అన్ని వీధులు శుభ్రం చేసి, మూగ్గులతో, తోరణాలతో, పువ్వులతో, చాలా అందంగా అలంకరించేవారు. 

 

ఊరేగింపుకు ఒక ఎద్దు బండి కట్టేవారు. ఆ బండిని కడిగి, పసుపు రాసి, బొట్లు పెట్టి, పూలు కట్టి దాన్ని కూడా అందంగా అలంకరించేవారు. 

 

మరి ఆ బండిని తోలే ఎద్దు సంగతి చెప్పాలా? ఊళ్ళో అన్నిటికన్నా ఆరోగ్య వంతంగా, బలంగా ఉన్న ఎద్దును ఎంచుకునేవారు. ఆ ఎద్దు చర్మం నిగనిగలాడేలా దానికి స్నానం చేయించి, బొట్లు పెట్టి, గంటలు కట్టి పట్టు వస్త్రాలు వేసేవారు. ఆహ! చాలా చూడ ముచ్చటగా తయారు చేసేవారు. 

 

ప్రతి సంవత్సరంలా ఈ సంవత్సరం కూడా ఊరేగింపుకు ఊరు తయారయ్యింది. రాముడు అనే ఓక ఎద్దును ఎంచుకున్నారు. బాగా తయారు చేసి, బండి కట్టారు. గుడి ముందర నుంచోపెట్టి, దేవుడి విగ్రహాన్ని బండిలో పెట్టి, హారతి ఇచ్చి ఊరేగింపు మొదలెట్టారు. 

 

ఆ రోజంతా రాముడు ఎక్కడికెళ్తే అక్కడ మనుషులు వంగి, నమస్కారాలు పెట్టారు. వెర్రి రాముడు ఇదంతా తనకి చేస్తున్న సత్కారం అనుకుని భ్రమ పడ్డాడు. రోజంతా చాలా గర్వంగా, పొగరుగా, కొమ్ములు పైకి పెట్టి, ఛాతీ బయిటికి పెట్టి నడిచాడు. తనలో తానె మురిసిపోయి, పొంగిపోయాడనుకోండి! 

 

ఇక సాయంత్రంతో మళ్ళి ఊరేగింపు గుడికి చేరింది. ఎదురు సన్నాహంతో, బాజా బజంత్రీలతో, గ్రామ ప్రజలు తమ దేవుడి విగ్రహాన్ని బండిలోంచి దింపి లోపలి తీలుకుని వెళ్లారు. 

 

విగ్రహం బండిలోంచి దిగంగానే ఇంకేముంది? అందరు రాముడిని మర్చిపోయారు. ఎవరి పనుల్లో వాళ్ళు పడిపోయారు. రాముడిపాయి వేసిన పట్టు వస్త్రాలు తీసేసి మళ్ళీ రాముడిని ఎడ్ల పాక లో తీసుకుని వెళ్లి అక్కడ వదిలేశారు. ఎవ్వరు దండాలు పెట్టలేదు. 

 

అప్పుడు రాముడికి అర్ధమయ్యింది. మనుషులు గౌరవం ఇచ్చేది మనకి కాదు, మనం చేసే పనులకని.ఒక రోజు ఒక గొర్రెలోడికి అనుకోకుండా ఒక పంది దొరికింది. 

 

గొర్రెలోడు వెంటనే ఆ పందిని పట్టడానికి ప్రయత్నం మొదలెట్టాడు. పందికి చాలా భయమేసింది. అది కేకలు పెడుతూ అటూ ఇటూ పరిగెత్తింది. నానా గోల పెట్టింది. 

 

ఎలాగో కష్ట పడి గొర్రెలోడు దాన్ని పట్టుకుని భుజం మీద వేసుకుని వేళ్ళ సాగాడు. అప్పు డైనా పంది గోల పెట్టడం ఆపిందా? లేదు. దాన్ని మానాన్ని అది వదలకుండా మహా గోల పెడుతూనే వుంది. భుజం మీద ఊరికే ఉండకుండా మెలికలు తిరుగుతూ కిందకి దుంకి పారిపోవాలని ప్రయత్నం చేస్తూనే ఉంది. 

 

అలా గోల గోల పెడుతున్న పందిని చూసి గొర్రెలోడి వెనకున్న గొర్రెలన్నీ నవ్వడం మొదలెట్టాయి. వాటిల్లో ఒక గొర్రె పందితో ఇలా అంది: “ఎందుకు అంత గోల పెడుతున్నావు? యెంత సిల్లీ గా కనిపిస్తున్నావో తెలుసా? ఈ గొర్రెలోడు మమ్మల్ని కూడా ఇలా పట్టుకుని నడుస్తాడు. కానీ మేము ఎప్పుడు ఇలా గోల గోల పెట్టము. మర్యాదగా చెప్పిన మాట వింటాము” 

 

వెనకున్న గొర్రెలన్నీ ఏదో ఎప్పుడు భయమంటే ఏంటో తెలీనట్టు మొహాలు పెట్టి తల ఊపుతున్నాయి. 

 

దానికి పంది ఇలా జవాబు చెప్పింది. “మిమ్మల్ని గొర్రె లోడు జాగ్రత్త గా చూసుకుంటాడు. మీకు స్నానం చేయించి, మేతకు తీసుకువెళ్లి, మిగతా జంతువుల నుంచి కాపాడి కంటికి రెప్పలా చూసుకుంటాడు. అందుకే మీకు అతనంటే భయం లేదు. కానీ నన్నేమి చేస్తాడో తెలీదు కదా? నన్ను వొండుకు తింటాడో, ఊళ్ళో అమ్మేస్తాడో ఏమిటో? నా భయం నాకు ఉంటుంది కదా!” నిజమే. ఏ అపాయం లేనప్పుడు ధైర్యంగా, సాహస మంతుల లా ఉండడం చాలా సులువు. ఆపద వచ్చినప్పుడు భయమంటే ఏంటో తెలుస్తుంది. అందుకే భయపడుతున్న వాళ్లని చూసి నవ్వకూడదు. వాళ్ళ కష్టం అర్ధం చేసుకోవాలి. 

 

""" 

 

# === CREATE OUTPUT FOLDER === 

output_folder = "tts_output" 

os.makedirs(output_folder, exist_ok=True) 

 

# === CREATE FILE NAMES USING VOICE + TEMPERATURE === 

# replace decimal point in temperature to avoid invalid filename characters 

temp_str = str(TEMPERATURE).replace('.', '_') 

filename_base = f"{VOICE_NAME}_temp{temp_str}" 

 

wav_file_path = os.path.join(output_folder, f"{filename_base}.wav") 

mp3_file_path = os.path.join(output_folder, f"{filename_base}.mp3") 

 

# === INITIALIZE CLIENT === 

client = genai.Client(api_key=API_KEY) 

 

# === GENERATE SPEECH === 

response = client.models.generate_content( 

    model="gemini-2.5-flash-preview-tts", 

    contents=STORY_TEXT, 

    config=types.GenerateContentConfig( 

        temperature=TEMPERATURE, 

        response_modalities=["AUDIO"], 

        speech_config=types.SpeechConfig( 

            voice_config=types.VoiceConfig( 

                prebuilt_voice_config=types.PrebuiltVoiceConfig( 

                    voice_name=VOICE_NAME 

                ) 

            ) 

        ), 

    ), 

) 

# === EXTRACT PCM DATA === 

data = response.candidates[0].content.parts[0].inline_data.data 

 

# === SAVE WAV FILE === 

with wave.open(wav_file_path, "wb") as wf: 

    wf.setnchannels(1) 

    wf.setsampwidth(2) 

    wf.setframerate(24000) 

    wf.writeframes(data) 

 

print(f" WAV file saved as: {wav_file_path}") 

 

# === CONVERT WAV → MP3 === 
audio_segment = AudioSegment.from_wav(wav_file_path) 
audio_segment.export(mp3_file_path, format="mp3", bitrate="192k") 
print(f" MP3 file saved as: {mp3_file_path}") 

