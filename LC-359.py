I really liked this problem because even though it is simple there are various solutions each with different trade-offs. While reviewing other people's solutions I took some notes I figured I might has well post them so other people can profit also.

Please upvote if you find this article useful, it will encourage me to write similar summaries for other problems ^_^

Simple HashMap

The simplest solution is to use a HashMap.

A great example of such a solution is:
class Logger(object):

    def __init__(self):
        self.ok = {}

    def shouldPrintMessage(self, timestamp, message):
        if timestamp < self.ok.get(message, 0):
            return False
        self.ok[message] = timestamp + 10
        return True

Time complexity

    O(1)

Space complexity

    O(n)

The disadvantage to this solution is that the memory usage never stops growing.

All the solutions below use different ways to manage the memory usage disadvantage mentioned above.

Use Two Sets

    def __init__(self):
        self.oldMessages = {}
        self.newerMessages = {}
        # We use this variable to keep track of the first message we added in either of the dictionaries.
        self.timeLastSeen = 0
        
    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        # If the current message is 20 seconds greater than the first message seen in olderMessages.
        if timestamp >= self.timeLastSeen + 20:
            self.oldMessages.clear()
            self.newerMessages.clear()
            self.timeLastSeen = timestamp
        # If the current message is 10 seconds greater than the first message seen in newerMessages.
        elif timestamp >= self.timeLastSeen + 10:
            self.oldMessages = self.newerMessages
            self.newerMessages = {}
            self.timeLastSeen = timestamp
        
        if message in self.newerMessages:
            return False
        if message in self.oldMessages and timestamp < self.oldMessages.get(message) + 10:
            return False
        self.newerMessages[message] = timestamp
        return True

This is my favorite. It's a simple implementation, it takes care of keeping memory usage low, and only requires swapping two HashMaps around.

Time complexity

    O(1)

Space complexity

    O(m) where m is the maximum number of unique message that will be received in a 20 second period.

Use a Queue and Set

https://leetcode.com/problems/logger-rate-limiter/discuss/349733/Simple-Java-solution-using-Queue-and-Set-for-slow-learners-like-myself

1- Use a Queue that contains Object(timestamp, message)
2- When new message comes in, remove from the Queue any message where timestamp + 10 < new message's timestamp. If any Queue element is deleted, remove that message from the Set (because the last occurence of this message is now too old)
3- If new message is still in Set, return false (because the Queue still contains it, so it is not too old yet)
4- Add the message to the Set

One downside is that if many unique messages are received in the 10 second window (say 1 million), the Queue can become very large. When it comes time to cleanup the Queue, the method will spend a lot time polling all messages off the Queue before returning. So in this example a lookuo that should be O(1) could be as bad as O(n) (where n is the number of records received, if we received 1 million records in the first 10 seconds)

Time complexity

    O(1)

Space complexity

    O(m) where m is the maximum number of unique message that will be received in a 10 second period.

Use Radix Sort and Buckets

https://leetcode.com/problems/logger-rate-limiter/discuss/83256/Java-Circular-Buffer-Solution-similar-to-Hit-Counter

It's a neat idea and fun to think about. It also takes care of keeping memory low but compared to the other solutions it's a bit more code and slightly less efficient, it's O(10n), which is the same as O(n) but still, that's up to 10x the number of lookups compared to a simple HashMap implementation.

Concurency / Thread safety

from multiprocessing import Semaphore


class Logger:
    def __init__(self):
        # message to last time seen
        # python dict is thread-safe
        self.m = {}
        self.lock = Semaphore(1)

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        self.lock.acquire()
        m = self.m
        if message not in m or timestamp - m[message] >= 10:
            m[message] = timestamp
            self.lock.release()
            return True

        self.lock.release()
        return False

It's possible that the Logger is called with the same message at the same time from multiple sources. In that case the HashMap might not have been updated fast enough when the second duplicate message arrives.

For example:

    New message m1 arrives at time 1
    Same message m1 arrives again at time 1
    Logger is called with (m1, 1)
    Logger is called with (m1, 1)
    The second call will possibly print the message if the first call (#3) hasn't had a chance to create the HashMap entry for m1 yet.