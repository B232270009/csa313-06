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
