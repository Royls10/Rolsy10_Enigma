import streamlit as st
import random
import string
import sys

# ==============================================================================
#  [CORE] 유니버설 에니그마 엔진 (변경 없음)
# ==============================================================================

# --- 문자셋 정의 ---
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

def setup_parts(seed, max_rotor_index):
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
#  [UI] Streamlit 웹 인터페이스 (사이드바 최적화 버전)
# ==============================================================================
def main():
    st.set_page_config(page_title="Universal Enigma", page_icon="🔐", layout="wide")

    # 세션 상태 초기화
    if 'rotor_order_val' not in st.session_state: st.session_state.rotor_order_val = "1 2 3"
    if 'initial_pos_val' not in st.session_state: st.session_state.initial_pos_val = "0 0 0"

    # ─────────────────────────────────────────────────────────────
    # [1] 사이드바: 설정 패널 (버튼 다이어트)
    # ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 1. Seed & Count
        seed_key = st.text_input("1. Seed", value="Royls_Secret", type="password")
        rotor_count = st.number_input("2. 로터 개수", min_value=1, value=3, step=1)

        if rotor_count >= 10000: st.warning("⚠️ 개수 과다 주의")
        if rotor_count >= 1000000: st.error("🚨 메모리 위험!")

        st.divider()

        # 2. 로터 순서
        st.subheader(f"3. 로터 순서")
        # [수정] 4개 -> 3개로 줄이고 이름 짧게 변경
        c1, c2, c3 = st.columns(3) 
        if c1.button("순차", key="ro_seq", use_container_width=True):
            st.session_state.rotor_order_val = " ".join([str(i+1) for i in range(rotor_count)])
        if c2.button("랜덤", key="ro_rnd", use_container_width=True):
            nums = list(range(1, rotor_count + 1))
            random.shuffle(nums)
            st.session_state.rotor_order_val = " ".join(map(str, nums))
        if c3.button("역순", key="ro_rev", use_container_width=True):
            st.session_state.rotor_order_val = " ".join([str(i) for i in range(rotor_count, 0, -1)])
        
        rotor_order_str = st.text_input("로터 순서", key="rotor_order_val", label_visibility="collapsed")

        # 검증
        ro_valid = True
        ro_error_msg = ""
        if not rotor_order_str.strip():
             ro_valid = False; ro_error_msg = "값 입력 필요"
        else:
            try:
                ro_list = list(map(int, rotor_order_str.split()))
                if len(ro_list) != rotor_count:
                    ro_valid = False; ro_error_msg = f"숫자 {len(ro_list)}개 (필요: {rotor_count})"
                elif len(set(ro_list)) != len(ro_list):
                    ro_valid = False; ro_error_msg = "중복 발생"
                elif any(n < 1 for n in ro_list):
                    ro_valid = False; ro_error_msg = "1 이상 숫자 필요"
            except: ro_valid = False; ro_error_msg = "형식 오류"

        if not ro_valid: st.error(f"❌ {ro_error_msg}")

        st.divider()

        # 3. 초기 위치
        limit = ALPHABET_SIZE - 1
        st.subheader(f"4. 초기 위치")
        # [수정] '000' 제거하고 '초기화'가 000 역할 수행, 3개 버튼 유지
        p1, p2, p3 = st.columns(3)
        if p1.button("순차", key="pos_seq", use_container_width=True):
             st.session_state.initial_pos_val = " ".join([str(i % (limit + 1)) for i in range(rotor_count)])
        if p2.button("랜덤", key="pos_rnd", use_container_width=True):
            st.session_state.initial_pos_val = " ".join([str(random.randint(0, limit)) for i in range(rotor_count)])
        if p3.button("리셋", key="pos_reset", use_container_width=True, help="모두 0으로 설정"):
            st.session_state.initial_pos_val = " ".join(["0"] * rotor_count)

        initial_pos_str = st.text_input("초기 위치", key="initial_pos_val", label_visibility="collapsed")

        # 검증
        pos_valid = True
        pos_error_msg = ""
        if not initial_pos_str.strip():
            pos_valid = False; pos_error_msg = "값 입력 필요"
        else:
            try:
                pos_list = list(map(int, initial_pos_str.split()))
                if len(pos_list) != rotor_count:
                    pos_valid = False; pos_error_msg = f"숫자 {len(pos_list)}개 (필요: {rotor_count})"
                else:
                    wrong = [i+1 for i, n in enumerate(pos_list) if not (0 <= n <= limit)]
                    if wrong: pos_valid = False; pos_error_msg = f"{wrong[0]}번째 범위 초과"
            except: pos_valid = False; pos_error_msg = "형식 오류"

        if not pos_valid: st.error(f"❌ {pos_error_msg}")
        
        st.caption(f"문자셋: {ALPHABET_SIZE}자 (0~{limit})")


    # ─────────────────────────────────────────────────────────────
    # [2] 메인 화면
    # ─────────────────────────────────────────────────────────────
    st.title("🌌 Universal Enigma Web")
    
    is_ready = seed_key and ro_valid and pos_valid

    if not is_ready:
        st.error("👈 왼쪽 설정 오류를 확인하세요.")

    tab1, tab2 = st.tabs(["🔒 암호화", "🔓 복호화"])

    def run_process(text, mode):
        try:
            with st.spinner('처리 중...'):
                final_ro = list(map(int, rotor_order_str.split()))
                final_pos = tuple(map(int, initial_pos_str.split()))
                ROTOR_BANK, REFLECTOR = setup_parts(seed_key, max(final_ro))
                machine = InfiniteEnigmaMachine([ROTOR_BANK[n] for n in final_ro], REFLECTOR, final_pos)
                processed = machine.process_text(text)
                return combine_hangul(processed)
        except Exception as e: return f"Error: {str(e)}"

    with tab1:
        text_in = st.text_area("평문 입력", height=200, placeholder="비밀 내용을 입력...", label_visibility="collapsed")
        if st.button("🚀 암호화", type="primary", disabled=not is_ready, use_container_width=True):
            if text_in:
                res = run_process(text_in, 'encrypt')
                st.success("결과:")
                st.code(res, language=None)
            else: st.warning("입력 필요")

    with tab2:
        cipher_in = st.text_area("암호문 입력", height=200, placeholder="암호문 붙여넣기...", label_visibility="collapsed")
        if st.button("🔓 복호화", type="secondary", disabled=not is_ready, use_container_width=True):
            if cipher_in:
                res = run_process(cipher_in, 'decrypt')
                st.success("결과:")
                st.code(res, language=None)
            else: st.warning("입력 필요")

if __name__ == "__main__":
    main()

