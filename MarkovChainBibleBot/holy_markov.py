
import re
import random

import get_bible


class Markov(object):
    def __init__(self, text):
        self.cache = {}
        self.words = text.split()
        self.word_size = len(self.words)
        self.database()

    def triples(self):
        """ Generates triples from the given data string. So if our string were
                "What a lovely day", we'd generate (What, a, lovely) and then
                (a, lovely, day).
        """

        if len(self.words) < 3:
            return

        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i + 1], self.words[i + 2])

    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]

    def generate_markov_text(self, size=25):
        seed = random.randint(0, self.word_size - 3)
        seed_word, next_word = self.words[seed], self.words[seed + 1]
        w1, w2 = seed_word, next_word
        gen_words = []
        for i in range(size):
            gen_words.append(w1)
            w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w2)

        return ' '.join(gen_words)


class BiblePassagesMarkov(Markov):
    passage_num_pattern = re.compile(r"\d+:\d+")
    passage_numbers = set()

    def __init__(self):
        bible_text = get_bible.read_gutenberg_bible()

        super().__init__(bible_text)
    
    def generate_markov_text(self, seed_words=None, min_words=25):

        # Process a user given seed_word
        seed_word_locations = [idx for idx, word in enumerate(self.words)
                                for seed_word in seed_words
                               if word.lower() == seed_word.lower()]
            
        if seed_word_locations:
            seed = random.choice(seed_word_locations)
        else:
            seed = random.randint(0, self.word_size - 3)
            
        w1, w2 = self.words[seed], self.words[seed + 1]
        gen_words = [w1.capitalize(), w2]
        # go until we have enough words and end in a period
        while w2[-1] != '.' or len(gen_words) < min_words:
            w1, w2 = w2, random.choice(self.cache[(w1, w2)])
            if self.passage_num_pattern.findall(w2):
                # Avoid adding passage numbers to the middle of the passage.
                # Also end a sentence when a passage number would have gone in.
                new_w1 = w1.replace(':', '.').replace(';', '.')
                gen_words[-1] = new_w1
            else:                
                gen_words.append(w2)

        return ' '.join(gen_words)

    def twitter_message(self, seed_words=None, line_length=140):
        if not self.passage_numbers:
            for word in self.words:
                found_pattern = self.passage_num_pattern.findall(word)
                if found_pattern:
                    self.passage_numbers.add(found_pattern[0])
        if seed_words is None:
            seed_words = []
        passage_num = random.sample(self.passage_numbers, 1)[0]
        seed_words += [passage_num]
        message = ''
        min_words = 18
        while len(message) > line_length or len(message) < 1:
            message = self.generate_markov_text(seed_words=seed_words, min_words=min_words)
            message = message.replace(passage_num+' ', '')

        return message


if __name__ == '__main__':
    bible_gen = BiblePassagesMarkov()
    for _ in range(10):
        print(bible_gen.twitter_message(seed_words=['follow', 'next', 'Andrew']))

