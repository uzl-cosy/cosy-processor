import json
import re


def count_syllables_german(word):
    """
    Count the number of syllables in a German word.

    :param word: The word to count syllables in
    :return: The number of syllables in the word
    """

    # German vowels and diphthongs (common combinations)
    syllable_pattern = r"[aeiouäöü]+|[aeiouäöü][^aeiouäöü\s]+"

    # Find all segments in the word that match the pattern
    syllables = re.findall(syllable_pattern, word.lower())

    # Adjust for e at the end of a word, which is often silent
    if word.lower().endswith("e"):
        return max(1, len(syllables) - 1)
    return max(1, len(syllables))


def calculate_sps_german(transcript):
    """
    Calculates the Syllable per Second (SPS) for each word in the German transcript.
    Each entry in the transcript list should be a tuple of (start_time, end_time, word).

    :param transcript: The transcript to calculate SPS for
    :return: A list of SPS values for each word in the transcript
    """
    sps_list = []
    for start_time, end_time, word in transcript:
        syllable_count = count_syllables_german(word)
        duration = end_time - start_time
        sps = syllable_count / duration if duration > 0 else 0
        sps_list.append(sps)

    return sps_list


def calculate_content_tempo(fa_input):
    """
    Calculate the content tempo for a German transcript.

    :param fa_input: The input data from the forced alignment
    :return: The tempo data
    """

    sentences = fa_input["Sentences"]
    word_start_times_for_sentences = []
    word_end_times_for_sentences = []
    last_index = 0
    for sentence in sentences:
        sentence_length = len(sentence.split(" "))
        word_start_times_for_sentences.append(
            fa_input["Word Start Times"][
                last_index : last_index + sentence_length
            ]
        )
        word_end_times_for_sentences.append(
            fa_input["Word End Times"][
                last_index : last_index + sentence_length
            ]
        )
        last_index = last_index + sentence_length
    calculate_sps_input_per_sentence = []
    for i, sentence in enumerate(sentences):
        calculate_sps_input_per_sentence.append(
            list(
                zip(
                    word_start_times_for_sentences[i],
                    word_end_times_for_sentences[i],
                    sentence.split(" "),
                )
            )
        )

    sps_per_sentence = []
    for sentence in calculate_sps_input_per_sentence:
        sps_per_sentence.append(calculate_sps_german(sentence))

    output = {
        "dataContinous": sps_per_sentence,
        "dataGlobal": [],
    }
    for sentence in sps_per_sentence:
        output["dataGlobal"].append(
            {
                "min": min(sentence),
                "max": max(sentence),
                "mean": sum(sentence) / len(sentence),
            }
        )
    return output


if __name__ == "__main__":
    input_file = "/Users/finnstoldt/Projects/laboratorium-cosy-v2/data/forcedalignment/www_1715355615-1.json"
    with open(input_file, "r") as j:
        input_json = json.loads(j.read())
    print(calculate_content_tempo(input_json))
