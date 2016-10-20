# Frequently Asked Questions

# Why isn’t this example with time.sleep() running in parallel?
# My code is asynchronous, but it’s not running in parallel in two browser tabs.
# Many people’s first foray into Tornado’s concurrency looks something like this:

class BadExampleHandler(RequestHandler):
    def get(self):
        for i in range(5):
            print(i)
            time.sleep(1)

# Fetch this handler twice at the same time and you’ll see that the second five-second countdown doesn’t start until the first one has completely finished. The reason for this is that time.sleep is a blocking function: it doesn’t allow control to return to the IOLoop so that other handlers can be run.
# Of course, time.sleep is really just a placeholder in these examples, the point is to show what happens when something in a handler gets slow. No matter what the real code is doing, to achieve concurrency blocking code must be replaced with non-blocking equivalents. This means one of three things:
# Find a coroutine-friendly equivalent. For time.sleep, use tornado.gen.sleep instead:

class CoroutineSleepHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        for i in range(5):
            print(i)
            yield gen.sleep(1)

#When this option is available, it is usually the best approach. See the Tornado wiki for links to asynchronous libraries that may be useful.

URL:统一资源定位符 也就是网址 例如 http://www.microsoft.com/ 
URI:通用资源标志符 http://www.acme.com/support/suppliers.htm;file://a:1234/b/c/d.txt