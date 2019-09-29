
class CascadeAnalyzer(object):
    def cascade_to_csv(self):
        out_file_name = OUT_PATH + 'temporal_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
        out_file = open(out_file_name, 'w', encoding='utf-8', newline='')
        writer = csv.writer(out_file)

        # Store loaded data
        df = self.meta_df  #
        cascades_dict = self.cascades_dict

        out_header = ['tweet_id', 'label',
                'avg_diffusion_time_from_src', 'avg_diffusion_time_from_root',
                'avg_retweet_diffusion_time_from_src', 'avg_retweet_diffusion_time_from_root',
                'avg_reply_diffusion_time_from_src', 'avg_reply_diffusion_time_from_root',
                'longest_length',
                ]


        writer.writerow(out_header)

        for index, row in df.iterrows():
            tweet_id = row['tweet_id']
            label = row['label']
            cascade = cascades_dict[tweet_id]

            # src_users = cascade.src_users
            # dst_users = cascade.dst_users

            avg_diffusion_time_from_src = cascade.average_diffusion_time_from_src
            avg_diffusion_time_from_root = cascade.average_diffusion_time_from_root
            avg_retweet_diffusion_time_from_src = cascade.average_retweet_diffusion_time_from_src
            avg_retweet_diffusion_time_from_root = cascade.average_retweet_diffusion_time_from_root
            avg_reply_diffusion_time_from_src = cascade.average_reply_diffusion_time_from_src
            avg_reply_diffusion_time_from_root = cascade.average_reply_diffusion_time_from_root

            # TODO TODO
            # writer.writerow([tweet_id, label, num_of_retweet, src_users_count, dst_users_count, retweet_count, response_count, net0, net1, net2, net3])
            writer.writerow([tweet_id, label,
                avg_diffusion_time_from_src, avg_diffusion_time_from_root,
                avg_retweet_diffusion_time_from_src, avg_retweet_diffusion_time_from_root,
                avg_reply_diffusion_time_from_src, avg_reply_diffusion_time_from_root,
                cascade.longest_length])

        out_file.close()

