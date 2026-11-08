import json,sys
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device='cpu',compute_type='int8',cpu_threads=4)
for i in sys.argv[2:]:
    import wave,numpy as np
    wf=wave.open(f'wav/v{i}.wav'); a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(a,language='pt',word_timestamps=True,vad_filter=False,beam_size=5,
        initial_prompt='Julia Roque, contadora. Contabilidade, faturamento, imposto, 13º salário, Black Friday, pró-labore.')
    words=[]; txt=[]
    for s in segs:
        txt.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        for w in s.words: words.append(dict(w=w.word.strip(),s=round(w.start,3),e=round(w.end,3)))
    json.dump(words,open(f'wav/v{i}.json','w'),ensure_ascii=False)
    open(f'wav/v{i}.txt','w').write('\n'.join(txt)); print('done',i,flush=True)
