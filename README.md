# Лаборатори 6 Category Partition ба PICT

Оюутны нэр: **Н. Төгөлдөр**  
Оюутны код: **B232270009**

Энэ ажил POST /transfer функцийн тест дизайныг category-partition болон PICT аргаар боловсруулна. Функцийн код байхгүй тул хүсэлтийг серверт ажиллуулсан үр дүн биш, тодорхойлолтоос гаргасан хүлээгдэх үр дүнг тайлагнана. PICT-ийн загваруудыг бодитоор ажиллуулсан.

## A1 Сонголт ба төлөөлөх утгууд

Setup: A данс U валюттай, үлдэгдэл B=1000 U, өдрийн нийт лимит L=800 U. B данс тусдаа, хүчинтэй. X данс байхгүй. Frozen үед A-г царцаана. Same валют нь U; Different валют нь V бөгөөд туршилтын тогтмол ханш 1 V=2 U. Эдгээр нь банкны бодит ханш биш, давтагдах тестийн fixture юм. Хөрвүүлсэн дүнг a гэж тэмдэглэв.

| Ангилал | Сонголт | Төлөөлөх утга | Тэмдэглэгээ ба үндэслэл |
|---|---|---|---|
| From | Valid | A, идэвхтэй | [IF/sourceExists]: дараагийн шалгалт хийх хүчинтэй эх үүсвэр. |
| From | Frozen | A, царцаатай | [ERROR_FROZEN]: шилжүүлэг хийх эрхгүй. |
| From | Missing | X | [ERROR_NO_FROM][SINGLE]: эх үүсвэр байхгүй нөхцөлийг нэг суурь тестээр тусгаарлана. |
| To | Valid | B | [IF/targetExists, distinct]: өөр хүчинтэй данс. |
| To | Missing | X | [ERROR_NO_TO]: хүлээн авагч байхгүй. |
| To | SameAsFrom | A (from=X бол X) | [ERROR_SAME_ACCOUNT][IF/sourceExists]: эх үүсвэр байгаа үед ижил дансны шалгалт утгатай. |
| Amount | Normal | a=100 U; U үед amount=100, V үед 50 | [IF/positive, affordable, withinLimit]: хоёр лимитэд багтана. |
| Amount | Zero | amount=0 | [ERROR_BAD_AMOUNT]: тэг дүн зөвшөөрөхгүй. |
| Amount | Negative | U үед -1, V үед -0.5 | [ERROR_BAD_AMOUNT]: сөрөг дүн зөвшөөрөхгүй. |
| Amount | OverBalance | a=1100; U үед 1100, V үед 550 | [ERROR_INSUFFICIENT]: B-ээс их; мөн лимит давна, үлдэгдлийг түрүүлж шалгана. |
| Amount | OverLimit | a=R+1; Fresh үед U=801/V=400.5, NearLimit үед U=201/V=100.5 | [ERROR_LIMIT][IF/affordable]: үлдэгдэлд багтах ч өдрийн үлдсэн лимит давна. |
| Currency | Same | U | [IF/rate=1]: хөрвүүлэлт шаардлагагүй. |
| Currency | Different | V | [IF/rate=2]: эхлээд U руу хөрвүүлж B, R-тэй харьцуулна. |
| Далд орчин Remaining | Fresh | өнөөдрийн зарцуулалт 0, R=800 | [IF/remaining=800]: лимитийг бүрэн ашиглаж болно. |
| Далд орчин Remaining | NearLimit | өнөөдрийн зарцуулалт 600, R=200 | [IF/remaining=200]: өмнөх шилжүүлгүүд шинэ хүсэлтийн лимитэд нөлөөлнө. |

Frozen нь from-ийн төлөв; SameAsFrom нь хоёр параметрийн харьцаа; Remaining нь хүсэлтийн body-д орохгүй орчны төлөв. Currency-ийн үл таних кодын алдааг тодорхойлолт өгөөгүй тул шинэ ERROR зохиогоогүй. Мөнгөний тооцоог аравтын бутархайгаар нарийвчлалтай хийж, энэ fixture-д бүх хөрвүүлэлт яг таарна.

## A2 Хязгаарлалт ба тооцоо

Алдааны давуу эрэмбэ: **NO_FROM → FROZEN → NO_TO → SAME_ACCOUNT → BAD_AMOUNT → INSUFFICIENT → LIMIT**; эхлээд дансны оршин байх ба эрхийг, дараа нь хүлээн авагчийг, эцэст нь хөрвүүлсэн мөнгөний хүрэлцээг шалгах нь утгатай тул энэ дарааллыг сонгов. Энэ нь спецификацид нэмсэн таамаг бөгөөд бодит хэрэгжүүлэлт батлагдсан гэсэн үг биш.

[ERROR] нь алдааны сонголтыг бусад алдааны сонголтоос тусгаарлана; OverBalance ганц сонголт боловч бодит хоёр дүрэм зөрчих тул эхний ERROR_INSUFFICIENT буцна. [SINGLE] Missing From-д To=Valid, Amount=Normal, Currency=Same, Remaining=Fresh гэсэн ганц төлөөлөх frame үлдээнэ. [IF/property] нь хөрвүүлсэн дүн, дансны харьцаа, үлдсэн лимитийн setup-ийг тогтооно. Эдгээр нь тест сонголтын бодлого бөгөөд хассан олон алдаатай хүсэлтүүд API-д өгөх боломжгүй гэсэн үг биш.

`transfer.model`-ийн дүрмүүд:

- From=Missing бол бусад бүх сонголтыг дээрх SINGLE суурь утгаар тогтооно.
- From=Frozen бол Amount=Normal, To=Valid; харин зориуд үлдээсэн To=Missing үед Currency=Same, Remaining=Fresh байна.
- To алдаатай бол Amount=Normal; From=Valid байна, зөвхөн Frozen+Missing давхар нөхцөлийг зөвшөөрнө.
- Amount алдаатай бол From=Valid, To=Valid байна.
- Frozen+To Missing+Normal+Same+Fresh нь давуу эрэмбийг шалгах нэг нэмэлт frame юм.

Бүрэн олонлог: **3 × 3 × 5 × 2 × 2 = 180**. Ердийн амжилтын frame 1×1×1×2×2=4; SINGLE Missing From=1; үлдсэн 7 алдааны сонголт тус бүр 2×2=4 frame буюу 28; зориудын давхар нөхцөл=1. Иймээс **180 → 4+1+28+1 = 34**. Энэ 34 нь бүх зөвшөөрсөн frame-ийн тоо; PICT-ийн pairwise гаралтын мөрийн тоотой адил байх албагүй.

## A3 Гараар боловсруулсан спецификаци

Хүснэгтийн Amount нь сонголтын нэр; бодит тоон дүнг A1-ийн setup-аас авна. Бүх ERROR-ийн HTTP статус 200, амжилтынх 201 байна.

| № | From | To | Amount | Currency | Remaining | Хүлээгдэх үр дүн |
|---|---|---|---|---|---|---|
| 1 | Valid | Valid | Normal | Same | Fresh | 201 OK |
| 2 | Valid | Valid | Normal | Different | NearLimit | 201 OK |
| 3 | Missing | Valid | Normal | Same | Fresh | 200 ERROR_NO_FROM, SINGLE |
| 4 | Frozen | Valid | Normal | Different | Fresh | 200 ERROR_FROZEN |
| 5 | Valid | Missing | Normal | Same | NearLimit | 200 ERROR_NO_TO |
| 6 | Valid | SameAsFrom | Normal | Different | Fresh | 200 ERROR_SAME_ACCOUNT |
| 7 | Valid | Valid | Zero | Same | Fresh | 200 ERROR_BAD_AMOUNT |
| 8 | Valid | Valid | Negative | Different | NearLimit | 200 ERROR_BAD_AMOUNT |
| 9 | Valid | Valid | OverBalance | Same | Fresh | 200 ERROR_INSUFFICIENT |
| 10 | Valid | Valid | OverLimit | Different | NearLimit | 200 ERROR_LIMIT |
| 11 | Frozen | Missing | Normal | Same | Fresh | 200 ERROR_FROZEN; NO_TO дарагдана |
| 12 | Valid | Valid | OverBalance | Different | NearLimit | 200 ERROR_INSUFFICIENT; LIMIT дарагдана |

Нэмэлт хил заагийн тестүүд (pairwise олонлогийн 180-д оруулаагүй): a=R=800 үед 201 OK; a=R+1=801 үед ERROR_LIMIT; a=B=1000 үед ERROR_LIMIT (үлдэгдэл хэтрээгүй); a=B+1=1001 үед ERROR_INSUFFICIENT. NearLimit үед a=200 нь 201 OK, a=201 нь ERROR_LIMIT. Эдгээрийг Same болон Different валютад хөрвүүлж давтах нь ≤ ба >-ийн хил, хөрвүүлэлтийн дарааллыг шалгана.

## B1 Браузерын pairwise ба 3 way

```bash
pict browser.model > results/browser-2way.txt
pict browser.model /o:3 > results/browser-3way.txt
```

| Загвар | Тестийн мөр (толгойг оруулаагүй) | Бүрэн олонлог | Хамрагдсан харилцан үйлчлэл |
|---|---:|---:|---:|
| Browser 2-way | 10 | 144 | 81/81 боломжит хос |
| Browser 3-way | 20 | 144 | 248/248 боломжит гурвал |

Браузерын бүрэн олонлог 3×3×2×2×2×2=144 байна. PICT-ийн 2-way гаралт 10 мөр тул лекцийн гараар хийсэн 9 мөрөөс нэгээр олон; PICT greedy алгоритмтай учраас хамгийн цөөн мөртэй шийдлийг заавал олдоггүй. Энэ нэмэлт мөр нь хосын хамралт дутуу гэсэн үг биш бөгөөд 81 боломжит хос бүгд хамрагдсаныг тусдаа шалгасан. 3-way нь 20 мөр буюу 2-way-аас хоёр дахин олон боловч 144-ийн 13.89% болж, бүрэн олонлогоос 124 мөрөөр цөөн байна.

## B2 Шилжүүлгийн гурван загвар

```bash
pict transfer-nc.model > results/transfer-nc.txt
pict transfer.model > results/transfer.txt
pict transfer-neg.model > results/transfer-neg.txt
```

| Загвар | Зөвшөөрсөн бүх frame | PICT мөр | Happy path | 1 алдааны сонголттой мөр | 2 алдааны сонголттой мөр | 3 алдааны сонголттой мөр | Нэг мөрийн хамгийн олон алдааны сонголт |
|---|---:|---:|---:|---:|---:|---:|---:|
| transfer-nc | 180 | 16 | 0 | 4 | 6 | 6 | 3 |
| transfer | 34 | 15 | 0 | 14 | 1 | 0 | 2 |
| transfer-neg | 33 | 20 | 4 | 16 | 0 | 0 | 1 |

Энд алдааны сонголтыг From≠Valid, To≠Valid, Amount≠Normal гэж тус бүр нэгээр тоолсон. Энэ нь зөрчсөн бизнес дүрмийн тоо биш: OverBalance нь ганц сөрөг утга боловч INSUFFICIENT болон LIMIT-ийг зэрэг зөрчинө. Иймд ~ нь сонголтын түвшний error masking-ийг багасгадаг ч бизнес дүрмийн давхардлыг бүрэн арилгахгүй. Missing From ба SameAsFrom зэрэг сонголтын үед to мөн байхгүй байж болно; хамгийн эхний NO_FROM л oracle болно.

Хязгаарлалтгүй загварын 16 мөр нь 87/87 хосыг хамардаг ч happy path үүсгээгүй. Хязгаарлалттай загвар 15 мөрөөр зөвшөөрсөн 66/66 хосыг хамарч, Frozen+Missing гэсэн зориудын давхар frame-ийг оруулсан; энэ хувилбарт мөн happy path алга. Pairwise нь бүх параметр зэрэг зөв байх frame-ийг заавал сонгохгүй тул A3-ийн happy path-уудыг тусад нь хадгална. Харин transfer-neg-ийн гаралтад дөрвөн эерэг Currency×Remaining хослол бүгд байгаа бөгөөд зөвшөөрсөн 65/65 хос хамрагдсан.

~ тэмдэглэгээ нь From, To, Amount-ийн алдааг нэг мөрөнд хамт оруулахгүй тул A2-ийн алдаа тусгаарлах ихэнх IF дүрмүүдийг давтах шаардлагагүй. Гэхдээ SINGLE Missing From-ийн Same/Fresh setup-ийг тогтоох IF дүрэм хэвээр хэрэгтэй; ~ дангаараа SINGLE гэсэн утгатай биш. Мөн хөрвүүлсэн мөнгөний утгыг setup-д бодох, үлдсэн лимитийг тогтоох, бодит домэйны хамаарлуудыг илэрхийлэх шаардлага хэвээр үлдэнэ. Зориудын Frozen+Missing давхар frame нь negative хувилбарт зөвшөөрөгдөхгүй учраас A3 болон transfer.model-д тусад нь байна. Хосын хамралтын баталгаа нь зөвхөн тухайн моделийн зөвшөөрсөн харилцан үйлчлэлд хамаарна; хассан олон алдаатай хослолд үйлчлэхгүй.

### PICT мөрөөс гаргасан бодит тест кейсүүд

Доорх мөрийн дугаар нь толгойг хассан **тестийн дугаар** (файлын мөрийн дугаар нь нэгээр их). Case бүрийг шинээр бэлдсэн орчинд бие даан ажиллуулах ёстой; өмнөх тестийн шилжүүлэг дараагийн тестийн үлдэгдэл, өдрийн лимитийг өөрчлөхгүй.

| Кейс | PICT эх мөр | Setup | POST /transfer body | Oracle |
|---|---|---|---|---|
| TC1 happy path | transfer-neg №1: Valid, Valid, Normal, Same, NearLimit | A идэвхтэй, 1000 U; B хүчинтэй; L=800, өмнөх зарцуулалт 600, R=200 | `{"from":"A","to":"B","amount":100,"currency":"U"}` | 201 `{"result":"OK"}`; 100≤1000 ба 100≤200 |
| TC2 нэг сөрөг сонголт | transfer-neg №5: Valid, Valid, ~OverLimit, Different, Fresh | A идэвхтэй, 1000 U; B хүчинтэй; L=800, зарцуулалт 0; 1 V=2 U | `{"from":"A","to":"B","amount":400.5,"currency":"V"}` | 200 `{"result":"ERROR_LIMIT"}`; хөрвүүлсний дараа 801 U≤1000 боловч >800 |
| TC3 давхар нөхцөл | transfer №9: Frozen, Missing, Normal, Same, Fresh | A царцаатай, 1000 U; X байхгүй; R=800 | `{"from":"A","to":"X","amount":100,"currency":"U"}` | 200 `{"result":"ERROR_FROZEN"}`; FROZEN нь NO_TO-оос өмнө |
| TC4 SINGLE | transfer-neg №18: ~Missing, Valid, Normal, Same, Fresh | X байхгүй; B хүчинтэй; суурь fixture R=800 | `{"from":"X","to":"B","amount":100,"currency":"U"}` | 200 `{"result":"ERROR_NO_FROM"}`; данс олдохгүй тул дараагийн шалгалт хийхгүй |

TC2 нь amount-ийг хүсэлтийн V валютаар өгч, 400.5-ыг шууд лимиттэй харьцуулах алдааг илрүүлэхээр загварчилсан. TC3 нь хоёр алдааны давуу эрэмбийг шалгана; ERROR_NO_TO салааг бие даан батлахын тулд A3 №5 шиг идэвхтэй эх данстай тест давхар хэрэгтэй.

## B3 Дүгнэлт

Category-partition нь дансны төлөв, мөнгөний хүрээ, валют, далд орчны сонголтыг утгаар нь ялгаж өгсөн. Гараар хийсэн A3 хүснэгт алдааны анги бүрийн oracle, SINGLE болон давхар нөхцөлийн давуу эрэмбийг тодорхой харуулсан. Харин гараар сонгосон цөөн мөр бүх хослолыг хамарсан гэсэн баталгаа өгөхгүй. PICT нь моделийн зөвшөөрсөн бүх хосыг хамардаг боловч бизнесийн зөв oracle-ийг өөрөө гаргахгүй. Хязгаарлалтгүй хувилбар олон алдааг нэг мөрөнд багтааж, аль шалгалтыг баталж байгаа нь error masking-ээс шалтгаалан бүдгэрсэн. Сөрөг утга ашиглахад нэг мөрийн алдааны сонголт нэг болж, энэ удаагийн гаралтад happy path ч бий болсон. Гэсэн ч OverBalance нь хоёр дүрэм зэрэг зөрчдөг учраас ~ тэмдэглэгээ бизнес дүрмүүдийн давхардлыг бүрэн шийдээгүй. Хамгийн их бодол шаардсан ажил нь хөрвүүлсний дараах дүн ба өдрийн үлдсэн лимитийг зөв төлөөлүүлж, хэт их хязгаарлалтаар чухал тестээ хасахгүй байх байсан. Иймээс хоёр аргыг хамтад нь хэрэглэж, гараар алдааны утга ба хил заагийг тодорхойлоод PICT-ээр зөвшөөрсөн харилцан үйлчлэлийн хамралтыг шалгах нь зохистой.

## Дахин ажиллуулах ба шалгах

PICT нь суусан хэрэгслийг ашигласан; суулгалт, build-ийг энэ ажлын хүрээнд дахин хийгээгүй. `results/pict-build.txt` нь байгаа эх кодын commit болон ажиллаж буй `pict` командын хэрэглээний эхний гурван мөрийг хадгалсан.

```bash
pict browser.model > results/browser-2way.txt
pict browser.model /o:3 > results/browser-3way.txt
pict transfer-nc.model > results/transfer-nc.txt
pict transfer.model > results/transfer.txt
pict transfer-neg.model > results/transfer-neg.txt
python3 verify_results.py
git log --oneline --reverse
```

`/r` сонголт ашиглаагүй. `verify_results.py` нь гаралтын давхардал, зөвшөөрсөн frame, бүх боломжит хос/гурвалын хамралт, дахин ажиллуулахад ижил гаралттай эсэх, negative мөр бүрийн алдааны сонголтын тоог шалгаж `results/verification.txt`-д хадгална. Мөн браузер ба nc/constrained загваруудыг `/o:max`-аар ажиллуулж, бүх frame-ийг тусдаа тооцоолсон олонлогтой тулгана. Энэ скрипт нь лабын үр дүнг шалгах туслах бөгөөд банкны функцийн хэрэгжүүлэлт эсвэл серверийн интеграцийн тест биш.

Зааврын `.docx`, PICT эх код, build хавтас нь `.gitignore`-д орсон. GitHub public репозиторид нийтлэх, Teams Assignment-д холбоос оруулж Turn in дарах үйлдлийг оюутан өөрөө гүйцэтгэнэ.
