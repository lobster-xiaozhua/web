import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const apiLatency = new Trend('api_latency', true);
const errorRate = new Rate('errors');

export const options = {
  scenarios: {
    reading: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 1000 },
        { duration: '1m', target: 3000 },
        { duration: '30s', target: 5000 },
        { duration: '1m', target: 5000 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
    searching: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 500 },
        { duration: '1m', target: 1500 },
        { duration: '30s', target: 2000 },
        { duration: '1m', target: 2000 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(99)<200'],
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost';

export default function () {
  // 阅读场景
  const novelRes = http.get(`${BASE_URL}/api/novels?page=1&size=20`);
  check(novelRes, { 'novels status 200': (r) => r.status === 200 });
  apiLatency.add(novelRes.timings.duration);
  errorRate.add(novelRes.status !== 200);
  sleep(Math.random() * 2);

  // 章节阅读
  const chapterRes = http.get(`${BASE_URL}/api/novels/1/chapters/1`);
  check(chapterRes, { 'chapter status 200': (r) => r.status === 200 || r.status === 404 });
  apiLatency.add(chapterRes.timings.duration);
  errorRate.add(chapterRes.status >= 500);
  sleep(Math.random() * 3);

  // 搜索场景
  const searchRes = http.get(`${BASE_URL}/api/search?q=修仙`);
  check(searchRes, { 'search status 200': (r) => r.status === 200 });
  apiLatency.add(searchRes.timings.duration);
  errorRate.add(searchRes.status !== 200);
  sleep(Math.random() * 2);
}
