import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.rcsetup as rcsetup
# print(rcsetup.all_backends)
# sns.set()
import os
def compile_data(data_path):
    data_path = '/home/thanos/tutorials/exercises/p4_FWB/out_data'
    files = os.listdir(data_path)
    gpp3_files = [file for file in files if file.startswith('3gpp_')]
    fwb_files = [file for file in files if file.startswith('pkt')]
    combined_data_file = 'combined_data.txt'
    wf = open(combined_data_file, "w")
    wf.write('FlowIdx,ArrivalTime,MulticastIdx,GWDelay,UEDelay,Protocol\n')
    protocol_name = '3GPP'
    for gpp_file in gpp3_files:
        rf = open(os.path.join(data_path, gpp_file))
        lines = rf.readlines()[1:2001]
        t0 = float(lines[0].split(',')[1])
        gw_delay = float(gpp_file.split('.')[0].split('_')[-2:][0].split('ms')[0])
        ue_delay = float(gpp_file.split('.')[0].split('_')[-2:][1].split('ms')[0])
        print('Writing GW: {}, UE:{}'.format(gw_delay,ue_delay))
        for line in lines:
            readings = line.split()[0].split(',')
            flow_idx = float(readings[0])
            flow_time = float(readings[2])
            flow_dst_id = float(readings[3])
            write_str = '{},{},{},{},{},{}\n'.format(flow_idx, flow_time - t0, flow_dst_id, gw_delay, ue_delay,
                                                     protocol_name)
            wf.write(write_str)
        rf.close()
    protocol_name = 'FWB'
    for fwb_file in fwb_files:
        rf = open(os.path.join(data_path, fwb_file))
        lines = rf.readlines()[1:2000]
        t0 = float(lines[0].split(',')[1])
        gw_delay = float(fwb_file.split('.')[0].split('_')[-2:][0].split('ms')[0])
        ue_delay = float(fwb_file.split('.')[0].split('_')[-2:][1].split('ms')[0])
        print('Writing GW: {}, UE:{}'.format(gw_delay,ue_delay))
        for line in lines:
            readings = line.split()[0].split(',')
            flow_idx = float(readings[0])
            flow_time = float(readings[2])
            flow_dst_id = float(readings[3])
            write_str = '{},{},{},{},{},{}\n'.format(flow_idx, flow_time - t0, flow_dst_id, gw_delay, ue_delay,
                                                     protocol_name)
            wf.write(write_str)
        rf.close()
    wf.close()


if __name__ == '__main__':
    data_path = '/home/thanos/tutorials/exercises/p4_FWB/out_data'
    compile_data(data_path)
    df = pd.read_csv('combined_data.txt')
    df['GW Delay (ms), UE Delay (ms)'] = df['GWDelay'].astype('int').astype('str')+ ', ' + df['UEDelay'].astype('int').astype('str')
    df_small = df[0:4000]
    df_ue = df.loc[df.loc[:, 'UEDelay'] == 500, :]
    sns.lineplot(x='Packet Index', y='Arrival Time', style='Protocol', hue='GW Delay (ms), UE Delay (ms)', data=df_ue.sort_values(['GWDelay']), markers=False)
    fig1 = plt.gcf()
    fig1.set_size_inches(18, 5.5)
    fig1.tight_layout()
    # figure_1,(ax1,ax2,ax3) = plt.subplots(nrows=1,ncols=3,sharey=True)
    # fig1 = sns.lineplot(x='Packet Index', y='Arrival Time', style='GW Delay, UE Delay', hue='Protocol', data=df.sort_values(['GWDelay','UEDelay']), markers=False)
    # fig1 = plt.gcf()
    # fig1.set_size_inches(18, 5.5)
    # fig1.tight_layout()

    plt.show()
    plt.savefig('Figure_1_gw_only.png')
