/**
 * =====================================================
 *  Google Apps Script - 청첩장 RSVP 백엔드
 * =====================================================
 *
 *  사용 방법:
 *  1. Google Sheets에서 새 스프레드시트를 생성합니다.
 *  2. 첫 번째 행(헤더)에 다음 항목을 입력합니다:
 *     A1: 제출시간 | B1: 성함 | C1: 참석여부 | D1: 참석인원 | E1: 축하메시지
 *  3. [확장 프로그램] > [Apps Script] 를 클릭합니다.
 *  4. 아래 코드를 전체 복사하여 붙여넣습니다.
 *  5. [배포] > [새 배포] > 유형: "웹 앱" 선택
 *     - 실행 주체: "나"
 *     - 액세스 권한: "모든 사용자"
 *  6. 배포 후 받은 웹 앱 URL을 복사합니다.
 *  7. 청첩장 HTML 파일의 GOOGLE_SCRIPT_URL 변수에 해당 URL을 붙여넣습니다.
 *
 * =====================================================
 */

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);

    sheet.appendRow([
      new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
      data.name || '',
      data.attendance || '',
      data.guests || '',
      data.message || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ result: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ result: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ result: 'success', message: 'RSVP API is running' }))
    .setMimeType(ContentService.MimeType.JSON);
}
