import Chance from 'chance';

const chance = new Chance.Chance();

interface Response {
    message: string;
}

export const main = async (): Promise<Response> => {
    return Promise.resolve({
        message: `Meet ${chance.name()}, a ${chance.animal()} who lives in ${chance.city()}!`,
    });
};
