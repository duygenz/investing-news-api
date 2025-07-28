import feedparser
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from operator import itemgetter

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS cho tất cả các domain, cho phép truy cập từ bất kỳ đâu
CORS(app)

# Danh sách các nguồn RSS cần tổng hợp
RSS_FEEDS = [
    'https://vn.investing.com/rss/market_overview_Fundamental.rss',
    'https://vn.investing.com/rss/market_overview_Technical.rss',
    'https://vn.investing.com/rss/market_overview_Opinion.rss',
    'https://vn.investing.com/rss/market_overview_investing_ideas.rss'
]

def parse_pubdate(pubdate_str):
    """
    Chuyển đổi chuỗi ngày tháng từ RSS feed sang đối tượng datetime.
    RSS feed sử dụng định dạng RFC 822.
    Ví dụ: 'Mon, 28 Jul 2025 08:00:00 GMT'
    """
    try:
        # strptime có thể xử lý hầu hết các định dạng ngày tháng phổ biến
        return datetime.strptime(pubdate_str, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError:
        # Trả về ngày hiện tại nếu không thể parse
        return datetime.now()

@app.route('/api/news', methods=['GET'])
def get_news():
    """
    API endpoint để lấy tin tức tổng hợp từ các nguồn RSS.
    """
    all_news = []
    seen_titles = set() # Sử dụng set để kiểm tra tiêu đề trùng lặp hiệu quả

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # Chỉ thêm tin tức nếu tiêu đề chưa tồn tại
                if entry.title not in seen_titles:
                    # Trích xuất hình ảnh từ media_content nếu có
                    image_url = None
                    if 'media_content' in entry and entry.media_content:
                        image_url = entry.media_content[0]['url']
                    
                    # Chuyển đổi ngày xuất bản
                    published_datetime = parse_pubdate(entry.published)

                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'description': entry.description,
                        'published': entry.published,
                        'published_datetime': published_datetime, # Thêm trường datetime để sắp xếp
                        'source': feed.feed.title,
                        'image': image_url
                    }
                    all_news.append(news_item)
                    seen_titles.add(entry.title)
        except Exception as e:
            # Ghi lại lỗi nếu có vấn đề khi fetch một feed
            print(f"Error fetching or parsing feed {feed_url}: {e}")

    # Sắp xếp danh sách tin tức theo ngày xuất bản, mới nhất lên đầu
    sorted_news = sorted(all_news, key=itemgetter('published_datetime'), reverse=True)

    # Xóa trường datetime đã dùng để sắp xếp trước khi trả về JSON
    for item in sorted_news:
        del item['published_datetime']

    return jsonify(sorted_news)

@app.route('/')
def index():
    """
    Trang chủ đơn giản để kiểm tra API có hoạt động không.
    """
    return "<h1>API Tổng hợp tin tức Investing.com</h1><p>Sử dụng endpoint <code>/api/news</code> để lấy dữ liệu.</p>"

if __name__ == '__main__':
    # Chạy ứng dụng ở chế độ debug khi phát triển ở local
    app.run(debug=True)
