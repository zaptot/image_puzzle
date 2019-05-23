import puzzle.crawler as crawler
import puzzle.processer as processer


def main():
    folder_with_images = "../images"
    count = 3000
    words = ["супергерои", "австралия", "космос"]
    image = "qwer.jpg"

    crawler_ = crawler.Crawler(folder_with_images)
    if not processer.get_all_images(folder_with_images):
        crawler_.get_images(count=count, folder=folder_with_images, words=words)

    processer.delete_bad_images(folder_with_images)
    processer.process_all_images(folder_with_images)
    processer.calc_signatures(folder_with_images)

    processer.make_puzzle(image=image, folder=folder_with_images)


if __name__ == "__main__":
    main()



