import streamlit as st
import random
import string
import sys
from collections import Counter
from io import StringIO

# ==============================================================================
#  [CORE] 유니버설 에니그마 엔진
# ==============================================================================
INITIAL_JAMO = [chr(c) for c in [0x3131, 0x3132, 0x3134, 0x3137, 0x3138, 0x3139, 0x3141, 0x3142, 0x3143, 0x3145, 0x3146, 0x3147, 0x3148, 0x3149, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e]]
MEDIAL_JAMO = [chr(c) for c in range(0x314f, 0x3164)]
FINAL_JAMO = [chr(c) for c in [0x3131, 0x3132, 0x3133, 0x3134, 0x3135, 0x3136, 0x3137, 0x3139, 0x313a, 0x313b, 0x313c, 0x313d, 0x313e, 0x313f, 0x3140, 0x3141, 0x3142, 0x3144, 0x3145, 0x3146, 0x3147, 0x3148, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e]]
ENGLISH_UPPER = list(string.ascii_uppercase)
ENGLISH_LOWER = list(string.ascii_lowercase)
NUMBERS = list(string.digits)
SPECIALS = list(" !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
MASTER_ALPHABET = sorted(list(set(INITIAL_JAMO + MEDIAL_JAMO + FINAL_JAMO + ENGLISH_UPPER + ENGLISH_LOWER + NUMBERS + SPECIALS)))
ALPHABET_SIZE = len(MASTER_ALPHABET)

CHOSEONG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSEONG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSEONG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
HANGUL_START = 0xAC00; JUNG_COUNT = 21; JONG_COUNT = 28

def split_syllables(s):
    decomposed = []
    for char in s:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            offset = code - HANGUL_START
            cho = offset // (JUNG_COUNT * JONG_COUNT)
            jung = (offset % (JUNG_COUNT * JONG_COUNT)) // JONG_COUNT
            jong = offset % JONG_COUNT
            decomposed.extend([INITIAL_JAMO[cho], MEDIAL_JAMO[jung]])
            if jong > 0: decomposed.append(FINAL_JAMO[jong - 1])
        else: decomposed.append(char)
    return "".join(decomposed)

def combine_hangul(text):
    result = []; length = len(text); i = 0
    while i < length:
        c1 = text[i]
        if c1 not in CHOSEONG_LIST or i + 1 >= length or text[i+1] not in JUNGSEONG_LIST:
            result.append(c1); i += 1; continue
        c2 = text[i+1]; cho, jung = CHOSEONG_LIST.index(c1), JUNGSEONG_LIST.index(c2); jong = 0; i += 2
        if i < length:
            c3 = text[i]
            if c3 in JONGSEONG_LIST:
                if not (i + 1 < length and text[i+1] in JUNGSEONG_LIST):
                    if i + 1 < length and (c3 + text[i+1]) in JONGSEONG_LIST: jong = JONGSEONG_LIST.index(c3 + text[i+1]); i += 2
                    else: jong = JONGSEONG_LIST.index(c3); i += 1
        result.append(chr(HANGUL_START + (cho * JUNG_COUNT * JONG_COUNT) + (jung * JONG_COUNT) + jong))
    return "".join(result)

class InfiniteEnigmaMachine:
    def __init__(self, rotors, reflector, positions):
        self.alphabet = MASTER_ALPHABET; self.size = len(self.alphabet)
        self.char_to_idx = {c: i for i, c in enumerate(self.alphabet)}
        self.rotors = [[self.char_to_idx[c] for c in r] for r in rotors]
        self.inverse_rotors = []
        for r in self.rotors:
            inv = [0] * self.size
            for inp, out in enumerate(r): inv[out] = inp
            self.inverse_rotors.append(inv)
        self.reflector = [self.char_to_idx[c] for c in reflector]
        self.positions = list(positions); self.num_rotors = len(self.rotors)

    def _step_rotors(self):
        rotate_next = True
        for i in range(self.num_rotors):
            if rotate_next:
                self.positions[i] = (self.positions[i] + 1) % self.size
                rotate_next = (self.positions[i] == 0)
            else: break

    def process_text(self, text):
        decomposed = split_syllables(text); result = []
        for char in decomposed:
            if char not in self.char_to_idx: result.append(char); continue
            self._step_rotors(); idx = self.char_to_idx[char]
            for i in range(self.num_rotors): 
                pos = self.positions[i]; idx = (idx + pos) % self.size
                idx = self.rotors[i][idx]; idx = (idx - pos + self.size) % self.size
            idx = self.reflector[idx]
            for i in range(self.num_rotors - 1, -1, -1):
                pos = self.positions[i]; idx = (idx + pos) % self.size
                idx = self.inverse_rotors[i][idx]; idx = (idx - pos + self.size) % self.size
            result.append(self.alphabet[idx])
        return "".join(result)

@st.cache_data(show_spinner=False)
def get_cached_parts(seed, max_rotor_index):
    random.seed(seed)
    base = list(MASTER_ALPHABET)
    rotor_bank = {}
    for i in range(1, max_rotor_index + 1):
        shuffled = random.sample(base, len(base))
        rotor_bank[i] = "".join(shuffled)
    unpaired = random.sample(base, len(base)); ref_map = {}
    for i in range(0, len(unpaired), 2):
        if i + 1 < len(unpaired): ref_map[unpaired[i]] = unpaired[i+1]; ref_map[unpaired[i+1]] = unpaired[i]
        else: ref_map[unpaired[i]] = unpaired[i]
    return rotor_bank, "".join(ref_map[c] for c in base)


# ==============================================================================
#  [Helper] 정밀 검증 함수
# ==============================================================================
def validate_input_precision(text, count, limit_val=None, type="rotor"):
    errors = []
    try:
        if not text.strip(): return ["값을 입력해주세요."]
        nums = list(map(int, text.split()))
        
        if len(nums) != count:
            return [f"개수 오류: 입력값은 {len(nums)}개인데, 로터 설정은 {count}개입니다."]
            
        for i, val in enumerate(nums):
            nth = f"{i+1}번째 숫자 {val}"
            if type == "rotor":
                if val < 1: errors.append(f"{nth}가 1보다 작습니다 (최소 1).")
                elif val > count: errors.append(f"{nth}가 로터 총 개수({count})를 초과했습니다.")
            elif type == "position":
                if val < 0: errors.append(f"{nth}가 0보다 작습니다.")
                elif val > limit_val: errors.append(f"{nth}가 문자셋 범위({limit_val})를 초과했습니다.")

        if type == "rotor":
            counter = Counter(nums)
            for num, cnt in counter.items():
                if cnt > 1:
                    indices = [str(i+1) for i, x in enumerate(nums) if x == num]
                    errors.append(f"숫자 {num}가 {', '.join(indices)}번째 위치에서 중복 사용되었습니다.")
    except ValueError: return ["숫자와 공백만 입력해야 합니다."]
    return errors


# ==============================================================================
#  [UI] Streamlit 웹 인터페이스
# ==============================================================================
def main():
    st.set_page_config(page_title="Universal Enigma v2.3", page_icon="🔐", layout="wide")

    # 상태 초기화
    if 'rotor_order_val' not in st.session_state: st.session_state.rotor_order_val = "1 2 3"
    if 'initial_pos_val' not in st.session_state: st.session_state.initial_pos_val = "0 0 0"
    if 'seed_val' not in st.session_state: st.session_state.seed_val = "Royls_Secret"
    if 'rotor_count_val' not in st.session_state: st.session_state.rotor_count_val = 3
    if 'last_op_mode' not in st.session_state: st.session_state.last_op_mode = None 
    if 'last_result' not in st.session_state: st.session_state.last_result = ""

    # ─────────────────────────────────────────────────────────────
    # [1] 사이드바
    # ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("⚙️ 시스템 제어")
        
        with st.expander("📥 설정 불러오기", expanded=False):
            import_code = st.text_input("Config Code", placeholder="Seed|Count|Order|Pos", label_visibility="collapsed")
            if st.button("적용하기", use_container_width=True):
                try:
                    parts = import_code.split('|')
                    if len(parts) == 4:
                        st.session_state.seed_val = parts[0]
                        st.session_state.rotor_count_val = int(parts[1])
                        st.session_state.rotor_order_val = parts[2]
                        st.session_state.initial_pos_val = parts[3]
                        st.session_state.last_op_mode = None
                        st.session_state.last_result = ""
                        st.success("동기화 완료")
                        st.rerun()
                    else: st.error("형식 오류")
                except: st.error("파싱 오류")

        st.divider()

        st.subheader("1. 핵심 코어")
        seed_key = st.text_input("Seed (보안 키)", key="seed_val", type="password")
        rotor_count = st.number_input("로터 개수", min_value=1, key="rotor_count_val", step=1)

        st.divider()

        st.subheader("2. 로터 순서")
        c1, c2, c3 = st.columns(3)
        if c1.button("순차", key="ro_seq"): st.session_state.rotor_order_val = " ".join([str(i+1) for i in range(rotor_count)])
        if c2.button("랜덤", key="ro_rnd"): nums = list(range(1, rotor_count + 1)); random.shuffle(nums); st.session_state.rotor_order_val = " ".join(map(str, nums))
        if c3.button("역순", key="ro_rev"): st.session_state.rotor_order_val = " ".join([str(i) for i in range(rotor_count, 0, -1)])
        
        rotor_order_str = st.text_input("로터 순서", key="rotor_order_val", label_visibility="collapsed")
        ro_errors = validate_input_precision(rotor_order_str, rotor_count, type="rotor")
        if ro_errors: 
            for err in ro_errors: st.error(f"❌ {err}")

        st.divider()

        limit = ALPHABET_SIZE - 1
        st.subheader(f"3. 초기 위치 (0~{limit})")
        p1, p2, p3 = st.columns(3)
        if p1.button("순차", key="pos_seq"): st.session_state.initial_pos_val = " ".join([str(i % (limit + 1)) for i in range(rotor_count)])
        if p2.button("랜덤", key="pos_rnd"): st.session_state.initial_pos_val = " ".join([str(random.randint(0, limit)) for i in range(rotor_count)])
        if p3.button("리셋", key="pos_reset"): st.session_state.initial_pos_val = " ".join(["0"] * rotor_count)
        
        initial_pos_str = st.text_input("초기 위치", key="initial_pos_val", label_visibility="collapsed")
        pos_errors = validate_input_precision(initial_pos_str, rotor_count, limit_val=limit, type="position")
        if pos_errors: 
            for err in pos_errors: st.error(f"❌ {err}")

        st.divider()
        
        is_ready = seed_key and not ro_errors and not pos_errors
        if is_ready:
            st.subheader("📤 설정 공유 코드")
            export_code = f"{seed_key}|{rotor_count}|{rotor_order_str}|{initial_pos_str}"
            st.code(export_code, language=None)

    # ─────────────────────────────────────────────────────────────
    # [2] 메인 작업 공간
    # ─────────────────────────────────────────────────────────────
    st.title("🌌 Universal Enigma v2.3")
    
    if not is_ready:
        st.warning("⚠️ 좌측 설정의 붉은색 오류를 해결해야 작동합니다.")
        st.stop()

    tab_text, tab_file = st.tabs(["📝 텍스트 처리", "📁 파일 처리"])

    def process_core(data_str):
        final_ro = list(map(int, rotor_order_str.split()))
        final_pos = tuple(map(int, initial_pos_str.split()))
        ROTOR_BANK, REFLECTOR = get_cached_parts(seed_key, max(final_ro))
        machine = InfiniteEnigmaMachine([ROTOR_BANK[n] for n in final_ro], REFLECTOR, final_pos)
        processed = machine.process_text(data_str)
        return combine_hangul(processed)

    # --- 텍스트 모드 ---
    with tab_text:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📥 입력")
            text_in = st.text_area("Input", height=350, label_visibility="collapsed")
            
            c_act1, c_act2 = st.columns(2)
            
            # [COLOR LOGIC] 버튼 색상 결정을 위한 동적 변수
            # 현재 상태가 ENC면 암호화버튼=Primary(강조), 아니면 Secondary
            enc_btn_type = "primary" if st.session_state.last_op_mode == "ENC" else "secondary"
            dec_btn_type = "primary" if st.session_state.last_op_mode == "DEC" else "secondary"
            
            # [BUTTONS] 동적 타입 적용
            if c_act1.button("🚀 암호화 (Encrypt)", type=enc_btn_type, use_container_width=True):
                if text_in:
                    st.session_state.last_result = process_core(text_in)
                    st.session_state.last_op_mode = "ENC"
                    st.rerun() # 색상 즉시 변경을 위해 재실행
            
            if c_act2.button("🔓 복호화 (Decrypt)", type=dec_btn_type, use_container_width=True):
                if text_in:
                    st.session_state.last_result = process_core(text_in)
                    st.session_state.last_op_mode = "DEC"
                    st.rerun() # 색상 즉시 변경을 위해 재실행

        with col2:
            if st.session_state.last_op_mode == "ENC":
                st.markdown("#### 🔒 :red[암호화 결과]")
                st.text_area("Output", value=st.session_state.last_result, height=350)
            elif st.session_state.last_op_mode == "DEC":
                st.markdown("#### 🔓 :blue[복호화 결과]")
                st.text_area("Output", value=st.session_state.last_result, height=350)
            else:
                st.markdown("#### 📤 결과 대기")
                st.text_area("Output", value="작업을 실행하세요.", height=350, disabled=True)

    # --- 파일 모드 ---
    with tab_file:
        st.info("텍스트 파일(.txt)을 업로드하여 내용을 변환합니다.")
        
        mode_select = st.radio(
            "작업 모드 선택:",
            ("암호화 (Encrypt)", "복호화 (Decrypt)"),
            horizontal=True
        )
        
        uploaded_file = st.file_uploader("파일 선택", type=['txt'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            string_data = uploaded_file.getvalue().decode("utf-8")
            st.caption(f"파일명: {uploaded_file.name} ({len(string_data)}자)")
            
            if st.button(f"🚀 {mode_select} 실행", type="primary", use_container_width=True):
                try:
                    res = process_core(string_data)
                    if "암호화" in mode_select:
                        st.success("🔒 암호화 완료! 다운로드하세요.")
                        st.download_button(
                            "💾 암호화 파일 다운로드 (encrypted.txt)", 
                            data=res.encode('utf-8'), 
                            file_name="encrypted.txt", 
                            mime="text/plain", use_container_width=True
                        )
                    else:
                        st.info("🔓 복호화 완료! 다운로드하세요.")
                        st.download_button(
                            "💾 복호화 파일 다운로드 (decrypted.txt)", 
                            data=res.encode('utf-8'), 
                            file_name="decrypted.txt", 
                            mime="text/plain", use_container_width=True
                        )
                except Exception as e:
                    st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
