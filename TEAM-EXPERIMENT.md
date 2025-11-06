# AI LAB NIGHT - DataOrigin
- Joaquin Montesinos

## Challenges
Google dork and parallelization in searching for a company's website based on a company name

## Tech Stack
python, browser_use, gpt5-high, composer1 y cursor

## Results and Conclusions
The page's search result was not as expected.
Google's captcha appeared several times after n requests.
At first it automatically switched to Bing and worked fine, but later Google's captcha blocked the browser and it became stuck.
I had to kill the process and restart it.
I tried rotating the browser's IP but I didn't have that option.
Browser-use only allows 3 concurrent instances. If you run more, it fails.
I tried creating 5 accounts to have 5 * 3 = 15 parallel instances.
I only spent €0.50 per account.
The result was 30/329.