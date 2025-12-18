import streamlit as st
import random
import string
import textwrap

# ==============================================================================
#  (기존 로직: 한글 처리 및 에니그마 클래스 - 동일하게 유지)
# ==============================================================================

# --- 문자셋 및 상수 ---
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
#  [UI] Streamlit 웹 인터페이스 (수정됨: 제한 해제)
# ==============================================================================
def main():
    st.set_page_config(page_title="Universal Enigma", page_icon="🔐")

    st.title("🌌 Universal Enigma Web")
    st.markdown("한글/영문/숫자 통합 지원 | 무한 로터 암호화 시스템")
    
    with st.sidebar:
        st.header("⚙️ 기계 설정 (Key Settings)")
        
        seed_key = st.text_input("1. 마스터 키 (Seed)", value="Royls_Secret", type="password")
        st.caption("※ 이 키가 같아야만 복호화가 가능합니다.")
        
        # [수정됨] max_value 제한을 제거하여 무제한 입력 가능
        rotor_count = st.number_input("2. 로터 개수", min_value=1, value=3, help="원하는 만큼 숫자를 올릴 수 있습니다.")
        
        default_order = " ".join([str(i+1) for i in range(rotor_count)])
        rotor_order_str = st.text_input(f"3. 로터 순서 ({rotor_count}개)", value=default_order)
        
        default_pos = "0 " * rotor_count
        initial_pos_str = st.text_input(f"4. 초기 위치 (0~{ALPHABET_SIZE-1})", value=default_pos.strip())
        
        st.info(f"현재 문자셋 크기: {ALPHABET_SIZE}자")

    # 메인 화면
    tab1, tab2 = st.tabs(["🔒 암호화 (Encrypt)", "🔓 복호화 (Decrypt)"])

    # 입력값 검증 및 처리 함수
    def run_enigma(text, mode):
        try:
            if not seed_key:
                st.error("Seed를 입력해주세요."); return None
            
            # 파싱
            order = list(map(int, rotor_order_str.split()))
            pos = tuple(map(int, initial_pos_str.split()))
            
            # 유효성 검사
            if len(order) != rotor_count: st.error(f"로터 순서 숫자가 {rotor_count}개여야 합니다."); return None
            if len(pos) != rotor_count: st.error(f"초기 위치 숫자가 {rotor_count}개여야 합니다."); return None
            if len(set(order)) != len(order): st.error("로터 순서에 중복된 번호가 있습니다."); return None
            
            # 실행
            with st.spinner('에니그마 가동 중...'):
                ROTOR_BANK, REFLECTOR = setup_parts(seed_key, max(order))
                machine = InfiniteEnigmaMachine([ROTOR_BANK[n] for n in order], REFLECTOR, pos)
                processed = machine.process_text(text)
                
            return combine_hangul(processed)
            
        except ValueError:
            st.error("숫자 입력 형식을 확인해주세요. (공백으로 구분)")
            return None
        except Exception as e:
            st.error(f"오류 발생: {e}")
            return None

    with tab1:
        st.subheader("메시지 암호화")
        plain_text = st.text_area("암호화할 내용을 입력하세요", height=150, placeholder="비밀 메시지 입력...")
        if st.button("암호화 실행", type="primary"):
            if plain_text:
                result = run_enigma(plain_text, 'encrypt')
                if result:
                    st.success("암호화 완료!")
                    st.code(result, language=None)
            else:
                st.warning("내용을 입력해주세요.")

    with tab2:
        st.subheader("메시지 복호화")
        cipher_text = st.text_area("복호화할 암호문을 입력하세요", height=150, placeholder="암호문 붙여넣기...")
        if st.button("복호화 실행"):
            if cipher_text:
                result = run_enigma(cipher_text, 'decrypt')
                if result:
                    st.success("복호화 완료!")
                    st.code(result, language=None)
            else:
                st.warning("내용을 입력해주세요.")

if __name__ == "__main__":
    main()
