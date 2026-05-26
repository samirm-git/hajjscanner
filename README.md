# 🕋 Hajj Scanner

Searches available hajj and umrah packages across various providers. 

## 🌐 Dashboard

👉 **[hajjumrahscanner.com](https://hajjumrahscanner.com)**

---

## ✨ Features

- Scrapes Hajj and Umrah package listings from major travel websites
- Extracts key fields: price, company, star rating, shifting status, hotel distance, and more
- Uploads structured data to AWS S3 for use by the dashboard
- Designed to be run on a schedule to keep data fresh

---

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- AWS credentials with write access to the target S3 bucket

### Installation

```bash
git clone https://github.com/your-username/hajjscanner.git
cd hajjscanner
```

### Configuration

Create a `.env` file in the root directory: CONTACT TO BECOME A CONTRIBUTOR
<!-- 
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-2
S3_BUCKET_NAME=your_bucket_name
``` -->

### Running the scraper

```bash
python -m scraper/pipeline.py
```

---

## ⚙️ Scheduling



---

## 🤝 Contributing

Contributions are welcome, especially new scrapers for additional travel websites. Here's how:

1. **Fork** this repository and clone your fork locally.
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```


### Ideas for contribution

- Scrapers for additional Hajj and Umrah travel websites
- Improved data cleaning and normalisation
- Error handling and retry logic for flaky requests
- Automated tests for scraper output validation

---

## 🔗 Related

- [HajjScanner Dashboard](https://github.com/your-username/hajjscanner-dashboard) — the Streamlit dashboard that visualises the data collected by this scraper


## 📄 License

This project is open source. See [LICENSE](LICENSE) for details.